"""Story generation: chat-template prompting, NER extraction, structured two-pass output, continuation memory."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional, Protocol

from loguru import logger

from config.settings import settings


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a warm, imaginative storyteller for children aged {age_range}. "
    "Your stories are short, age-appropriate, and have a clear beginning, "
    "middle, and end. They contain no violence, no scary content, no adult "
    "themes, and no frightening imagery. The tone is {tone}. Stories should "
    "feel complete — never trailing off mid-sentence. Use simple, vivid "
    "language a child can follow."
)


def _outline_user_prompt(user_request: str, entities: List[str]) -> str:
    entities_hint = f"\nKey elements to include: {', '.join(entities)}." if entities else ""
    return (
        f"A child has asked for a story: \"{user_request}\".{entities_hint}\n\n"
        "Sketch a short outline as 5 bullet points covering: "
        "(1) characters, (2) setting, (3) what they want, "
        "(4) the problem or surprise, (5) how it resolves happily. "
        "Just the bullets, no preamble."
    )


def _story_user_prompt(user_request: str, entities: List[str], outline: Optional[str], moral: Optional[str]) -> str:
    parts = [f"A child has asked for a story: \"{user_request}\"."]
    if entities:
        parts.append(f"Include these elements naturally: {', '.join(entities)}.")
    if outline:
        parts.append(f"Follow this outline:\n{outline}")
    if moral:
        parts.append(f"End with a gentle lesson about: {moral}.")
    parts.append(
        "Write the full story now. Begin directly with the story — no title, "
        "no preamble, no commentary. Keep it to roughly 200–300 words and end "
        "with a satisfying conclusion."
    )
    return "\n\n".join(parts)


def _continuation_user_prompt(follow_up: str) -> str:
    return (
        f"Continue the story naturally based on what came before. "
        f"The child says: \"{follow_up}\". Write the next part directly — "
        "no recap, no preamble. Keep the same tone and characters, "
        "and bring this segment to a satisfying mini-conclusion."
    )


def _critique_user_prompt(user_request: str, story: str, age_range: str) -> str:
    return (
        f"You are reviewing a children's story for a child aged {age_range}.\n\n"
        f"Original request: \"{user_request}\"\n\n"
        f"Story:\n{story}\n\n"
        "Evaluate strictly against these criteria:\n"
        "1. Age-appropriate (no scary, violent, or adult content).\n"
        "2. Coherent narrative arc (clear beginning, middle, end).\n"
        "3. Vivid and engaging (concrete imagery, not bland or repetitive).\n"
        "4. Complete (no trailing off; satisfying ending).\n"
        "5. Honors the original request.\n\n"
        "Reply in exactly this format and nothing else:\n"
        "ISSUES:\n"
        "- <one specific issue per line, or write 'none' if there are no issues>\n"
        "VERDICT: GOOD"
        " (use GOOD if the story is solid, NEEDS_WORK if revisions are required)"
    )


def _revise_user_prompt(user_request: str, story: str, issues: str) -> str:
    return (
        "Revise this children's story to address the listed issues. "
        "Keep what works; fix only what's broken.\n\n"
        f"Original request: \"{user_request}\"\n\n"
        f"Current story:\n{story}\n\n"
        f"Issues to fix:\n{issues}\n\n"
        "Write the full revised story now. Begin directly with the story — "
        "no preamble, no commentary, no titles."
    )


# ---------------------------------------------------------------------------
# Entity extraction (spaCy with graceful fallback)
# ---------------------------------------------------------------------------

class _EntityExtractor:
    """Lazy spaCy extractor; falls back to identity if spaCy/model not available."""

    def __init__(self) -> None:
        self._nlp = None
        self._tried_load = False

    def _ensure_loaded(self) -> None:
        if self._tried_load:
            return
        self._tried_load = True
        try:
            import spacy

            try:
                self._nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy en_core_web_sm loaded for entity extraction.")
            except OSError:
                logger.warning(
                    "spaCy model 'en_core_web_sm' not installed. "
                    "Run: python -m spacy download en_core_web_sm"
                )
        except ImportError:
            logger.warning("spaCy not installed; entity extraction will pass user text through unchanged.")

    def extract(self, text: str) -> List[str]:
        self._ensure_loaded()
        if self._nlp is None:
            return []
        doc = self._nlp(text)
        out: List[str] = []
        seen = set()
        for ent in doc.ents:
            phrase = ent.text.strip()
            if phrase and phrase.lower() not in seen:
                seen.add(phrase.lower())
                out.append(phrase)
        for chunk in doc.noun_chunks:
            phrase = chunk.text.strip()
            if not phrase or phrase.lower() in seen:
                continue
            seen.add(phrase.lower())
            out.append(phrase)
        return out


# ---------------------------------------------------------------------------
# Backends
# ---------------------------------------------------------------------------

@dataclass
class GenerationParams:
    max_new_tokens: int = settings.MAX_STORY_LENGTH
    temperature: float = settings.TEMPERATURE
    top_p: float = settings.TOP_P


@dataclass
class Critique:
    """Parsed verdict from the critique pass."""
    is_good_enough: bool
    issues: List[str]
    raw: str


@dataclass
class Message:
    role: str  # "system" | "user" | "assistant"
    content: str


class Backend(Protocol):
    def chat(self, messages: List[Message], params: GenerationParams) -> str: ...


# ---------------------------------------------------------------------------
# Debug logging wrapper for LLM calls
# ---------------------------------------------------------------------------

class LoggingBackend:
    """Wraps any Backend to print every LLM call's input and output to stdout."""

    _DIVIDER = "=" * 72
    _SUBDIVIDER = "-" * 72

    def __init__(self, inner: Backend) -> None:
        self._inner = inner
        self._call_count = 0

    def chat(self, messages: List[Message], params: GenerationParams) -> str:
        self._call_count += 1
        n = self._call_count
        self._print_input(n, messages, params)
        response = self._inner.chat(messages, params)
        self._print_output(n, response)
        return response

    @classmethod
    def _print_input(cls, n: int, messages: List[Message], params: GenerationParams) -> None:
        print(f"\n{cls._DIVIDER}")
        print(f"LLM CALL #{n}  |  INPUT")
        print(f"params: max_new_tokens={params.max_new_tokens} "
              f"temperature={params.temperature} top_p={params.top_p}")
        print(cls._SUBDIVIDER)
        for m in messages:
            print(f"[{m.role}]")
            print(m.content)
            print()
        print(cls._DIVIDER)

    @classmethod
    def _print_output(cls, n: int, response: str) -> None:
        print(f"\n{cls._DIVIDER}")
        print(f"LLM CALL #{n}  |  OUTPUT  ({len(response)} chars, {len(response.split())} words)")
        print(cls._SUBDIVIDER)
        print(response)
        print(f"{cls._DIVIDER}\n")


class LocalBackend:
    """HuggingFace transformers backend with optional 4-bit quantization."""

    def __init__(self, model_name: str, use_quantization: bool = True) -> None:
        self.model_name = model_name
        self.use_quantization = use_quantization
        self._tokenizer = None
        self._model = None
        self._load()

    def _load(self) -> None:
        from transformers import AutoModelForCausalLM, AutoTokenizer

        logger.info(f"Loading local model: {self.model_name}")
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        if self._tokenizer.pad_token_id is None:
            self._tokenizer.pad_token_id = self._tokenizer.eos_token_id

        kwargs: dict = {"trust_remote_code": True}
        if self.use_quantization:
            try:
                import bitsandbytes  # noqa: F401  -- presence check; raises on Windows / no-CUDA
                import torch
                from transformers import BitsAndBytesConfig

                if not torch.cuda.is_available():
                    raise RuntimeError("CUDA not available; bitsandbytes 4-bit requires a GPU.")

                kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                )
                kwargs["device_map"] = "auto"
                logger.info("Using 4-bit quantization via bitsandbytes.")
            except Exception as e:
                logger.warning(f"bitsandbytes unavailable ({e}); falling back to full precision on CPU.")

        self._model = AutoModelForCausalLM.from_pretrained(self.model_name, **kwargs)
        logger.info(f"Local model {self.model_name} ready.")

    def chat(self, messages: List[Message], params: GenerationParams) -> str:
        msg_dicts = [{"role": m.role, "content": m.content} for m in messages]
        prompt_text = self._tokenizer.apply_chat_template(
            msg_dicts, tokenize=False, add_generation_prompt=True
        )

        inputs = self._tokenizer(prompt_text, return_tensors="pt")
        if hasattr(self._model, "device"):
            inputs = {k: v.to(self._model.device) for k, v in inputs.items()}

        output_ids = self._model.generate(
            **inputs,
            max_new_tokens=params.max_new_tokens,
            temperature=params.temperature,
            top_p=params.top_p,
            do_sample=True,
            repetition_penalty=1.15,
            no_repeat_ngram_size=3,
            pad_token_id=self._tokenizer.pad_token_id,
        )

        input_len = inputs["input_ids"].shape[1]
        new_tokens = output_ids[0][input_len:]
        return self._tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


class LlamaCppBackend:
    """GGUF-quantized local backend via llama-cpp-python (CPU-friendly, no CUDA needed)."""

    def __init__(
        self,
        model_path: Optional[str] = None,
        model_repo: Optional[str] = None,
        model_file: Optional[str] = None,
        n_ctx: int = 4096,
        n_threads: Optional[int] = None,
    ) -> None:
        from llama_cpp import Llama

        if model_path:
            logger.info(f"Loading GGUF model from local path: {model_path}")
            self._llm = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_threads=n_threads,
                verbose=False,
            )
        elif model_repo and model_file:
            logger.info(f"Loading GGUF model from HF: {model_repo} / {model_file}")
            self._llm = Llama.from_pretrained(
                repo_id=model_repo,
                filename=model_file,
                n_ctx=n_ctx,
                n_threads=n_threads,
                verbose=False,
            )
        else:
            raise RuntimeError(
                "LlamaCppBackend requires either LLAMA_CPP_MODEL_PATH or "
                "both LLAMA_CPP_MODEL_REPO and LLAMA_CPP_MODEL_FILE."
            )
        logger.info("llama-cpp-python backend ready.")

    def chat(self, messages: List[Message], params: GenerationParams) -> str:
        msg_dicts = [{"role": m.role, "content": m.content} for m in messages]
        resp = self._llm.create_chat_completion(
            messages=msg_dicts,
            max_tokens=params.max_new_tokens,
            temperature=params.temperature,
            top_p=params.top_p,
            repeat_penalty=1.15,
        )
        return resp["choices"][0]["message"]["content"].strip()


class AnthropicBackend:
    """Claude API backend for higher-quality stories."""

    def __init__(self, model: str, api_key: Optional[str] = None) -> None:
        from anthropic import Anthropic

        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY not set; cannot use anthropic backend.")
        self._client = Anthropic(api_key=key)
        self.model = model
        logger.info(f"Anthropic backend ready with model {model}.")

    def chat(self, messages: List[Message], params: GenerationParams) -> str:
        system = next((m.content for m in messages if m.role == "system"), None)
        turns = [{"role": m.role, "content": m.content} for m in messages if m.role != "system"]
        resp = self._client.messages.create(
            model=self.model,
            system=system or "",
            messages=turns,
            max_tokens=params.max_new_tokens,
            temperature=params.temperature,
            top_p=params.top_p,
        )
        return "".join(block.text for block in resp.content if hasattr(block, "text")).strip()


# ---------------------------------------------------------------------------
# Story generator + conversation memory
# ---------------------------------------------------------------------------

@dataclass
class StoryConversation:
    """Tracks prior turns so the bot can continue a story."""
    turns: List[Message] = field(default_factory=list)
    limit: int = settings.CONVERSATION_HISTORY_LIMIT

    def add(self, role: str, content: str) -> None:
        self.turns.append(Message(role=role, content=content))
        if len(self.turns) > self.limit * 2:
            self.turns = self.turns[-self.limit * 2 :]

    def reset(self) -> None:
        self.turns.clear()

    @property
    def history(self) -> List[Message]:
        return list(self.turns)


class StoryGenerator:
    """Kids' storyteller with pluggable backend, NER input parsing, structured generation, and continuation memory."""

    def __init__(
        self,
        model_name: str = settings.TEXT_GENERATION_MODEL,
        backend: str = settings.STORY_BACKEND,
        use_quantization: bool = settings.USE_QUANTIZATION,
    ) -> None:
        self.model_name = model_name
        self._extractor = _EntityExtractor()
        self._conversation = StoryConversation()
        self.backend: Backend = self._build_backend(backend, model_name, use_quantization)

    @staticmethod
    def _build_backend(backend: str, model_name: str, use_quantization: bool) -> Backend:
        if backend == "anthropic":
            inner: Backend = AnthropicBackend(
                model=settings.ANTHROPIC_MODEL, api_key=settings.ANTHROPIC_API_KEY
            )
        elif backend == "local":
            inner = LocalBackend(model_name=model_name, use_quantization=use_quantization)
        elif backend == "llama_cpp":
            inner = LlamaCppBackend(
                model_path=settings.LLAMA_CPP_MODEL_PATH,
                model_repo=settings.LLAMA_CPP_MODEL_REPO,
                model_file=settings.LLAMA_CPP_MODEL_FILE,
                n_ctx=settings.LLAMA_CPP_N_CTX,
                n_threads=settings.LLAMA_CPP_N_THREADS,
            )
        else:
            raise ValueError(f"Unknown STORY_BACKEND: {backend!r}")

        if settings.LOG_LLM_CALLS:
            logger.info("LLM call logging enabled (LOG_LLM_CALLS=True).")
            return LoggingBackend(inner)
        return inner

    # -- public API ---------------------------------------------------------

    def extract_entities(self, text: str) -> List[str]:
        return self._extractor.extract(text)

    def generate_story_from_input(self, user_input: str) -> str:
        """Entry point used by bot.py: builds a fresh story from user text."""
        return self.start_new_story(user_input)

    def start_new_story(
        self,
        user_request: str,
        age_range: str = settings.DEFAULT_AGE_RANGE,
        tone: str = settings.DEFAULT_TONE,
        moral: Optional[str] = None,
        structured: bool = settings.STRUCTURED_GENERATION,
        refine_rounds: Optional[int] = None,
        params: Optional[GenerationParams] = None,
    ) -> str:
        params = params or GenerationParams()
        rounds = settings.STORY_REFINEMENT_ROUNDS if refine_rounds is None else refine_rounds
        self._conversation.reset()

        entities = self._extractor.extract(user_request)
        if entities:
            logger.info(f"Extracted entities: {entities}")
        else:
            logger.info("No entities extracted; using raw user text as the prompt body.")

        system = SYSTEM_PROMPT.format(age_range=age_range, tone=tone)

        outline: Optional[str] = None
        if structured:
            outline_messages = [
                Message("system", system),
                Message("user", _outline_user_prompt(user_request, entities)),
            ]
            outline_params = GenerationParams(max_new_tokens=180, temperature=0.7, top_p=params.top_p)
            outline = self.backend.chat(outline_messages, outline_params).strip()
            logger.info(f"Outline generated ({len(outline.split())} words).")

        story_user_msg = _story_user_prompt(user_request, entities, outline, moral)
        story_messages = [Message("system", system), Message("user", story_user_msg)]
        story = self.backend.chat(story_messages, params).strip()
        logger.info(f"Draft story generated ({len(story.split())} words).")

        if rounds > 0:
            story = self.refine_story(
                story=story,
                user_request=user_request,
                rounds=rounds,
                age_range=age_range,
                system=system,
                params=params,
            )

        self._conversation.add("system", system)
        self._conversation.add("user", story_user_msg)
        self._conversation.add("assistant", story)

        return story

    # -- critique-revise loop ----------------------------------------------

    def refine_story(
        self,
        story: str,
        user_request: str,
        rounds: int = 1,
        age_range: str = settings.DEFAULT_AGE_RANGE,
        system: Optional[str] = None,
        params: Optional[GenerationParams] = None,
    ) -> str:
        """Critique-revise loop. Stops early if the critique returns VERDICT: GOOD."""
        if rounds <= 0:
            return story
        params = params or GenerationParams()
        system = system or SYSTEM_PROMPT.format(age_range=age_range, tone=settings.DEFAULT_TONE)

        current = story
        for i in range(1, rounds + 1):
            critique = self._critique_story(current, user_request, age_range, system)
            logger.info(
                f"Refinement round {i}/{rounds}: "
                f"{'GOOD' if critique.is_good_enough else 'NEEDS_WORK'} "
                f"({len(critique.issues)} issue(s))"
            )
            if critique.is_good_enough or not critique.issues:
                logger.info(f"Stopping refinement at round {i}: critique passed.")
                break
            current = self._revise_story(current, user_request, critique, system, params)
            logger.info(f"Revised story (round {i}): {len(current.split())} words.")

        return current

    def _critique_story(
        self,
        story: str,
        user_request: str,
        age_range: str,
        system: str,
    ) -> Critique:
        messages = [
            Message("system", system),
            Message("user", _critique_user_prompt(user_request, story, age_range)),
        ]
        critique_params = GenerationParams(max_new_tokens=220, temperature=0.3, top_p=0.9)
        raw = self.backend.chat(messages, critique_params).strip()
        return self._parse_critique(raw)

    @staticmethod
    def _parse_critique(raw: str) -> Critique:
        """Parse the structured critique output. Robust to small-model formatting drift."""
        upper = raw.upper()
        # Find the VERDICT marker if the model emitted one.
        verdict_idx = upper.rfind("VERDICT")
        verdict_is_good = False
        if verdict_idx != -1:
            tail = upper[verdict_idx:]
            # GOOD wins only if it appears and NEEDS_WORK doesn't appear closer to the verdict.
            good_pos = tail.find("GOOD")
            bad_pos = tail.find("NEEDS_WORK")
            if good_pos != -1 and (bad_pos == -1 or good_pos < bad_pos):
                verdict_is_good = True

        # Pull bullet/dash lines under an ISSUES heading; otherwise grab all bullet lines.
        issues: List[str] = []
        in_issues = False
        for line in raw.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            upper_line = stripped.upper()
            if upper_line.startswith("ISSUES"):
                in_issues = True
                continue
            if upper_line.startswith("VERDICT"):
                in_issues = False
                continue
            if in_issues or stripped.startswith(("-", "*", "•")):
                cleaned = stripped.lstrip("-*• ").strip()
                if cleaned and cleaned.lower() != "none":
                    issues.append(cleaned)

        # Heuristic backstop: if no VERDICT marker, treat "no issues" as good.
        if verdict_idx == -1 and not issues:
            verdict_is_good = True

        return Critique(is_good_enough=verdict_is_good, issues=issues, raw=raw)

    def _revise_story(
        self,
        story: str,
        user_request: str,
        critique: Critique,
        system: str,
        params: GenerationParams,
    ) -> str:
        issues_block = "\n".join(f"- {iss}" for iss in critique.issues) or "- (general polish)"
        messages = [
            Message("system", system),
            Message("user", _revise_user_prompt(user_request, story, issues_block)),
        ]
        # Slightly lower temperature for revision — we want fixes, not new randomness.
        revise_params = GenerationParams(
            max_new_tokens=params.max_new_tokens,
            temperature=max(0.3, params.temperature - 0.2),
            top_p=params.top_p,
        )
        return self.backend.chat(messages, revise_params).strip()

    def continue_story(
        self,
        follow_up: str = "What happens next?",
        params: Optional[GenerationParams] = None,
    ) -> str:
        if not self._conversation.turns:
            logger.warning("No prior story; starting a new one from the follow-up.")
            return self.start_new_story(follow_up)

        params = params or GenerationParams()
        messages = list(self._conversation.turns)
        messages.append(Message("user", _continuation_user_prompt(follow_up)))

        continuation = self.backend.chat(messages, params).strip()
        logger.info(f"Continuation generated ({len(continuation.split())} words).")

        self._conversation.add("user", _continuation_user_prompt(follow_up))
        self._conversation.add("assistant", continuation)
        return continuation

    @property
    def history(self) -> List[Message]:
        return self._conversation.history
