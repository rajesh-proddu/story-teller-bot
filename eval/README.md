# Story Teller Bot - Evaluation Harness

A small, reproducible eval that lets you compare two versions of the story
generator (e.g. before and after a prompt change, model swap, or sampling
tweak).

## What it does

1. **Generate** - Runs `StoryGenerator().generate_story_from_input()` against
   the 20 fixed prompts in `prompts.json` and saves the stories plus timing.
2. **Score** - Asks an Anthropic judge LLM
   (`claude-haiku-4-5-20251001`) to rate each story 1-5 on four axes
   (coherence, age-appropriateness, completeness, creativity). Falls back to a
   transparent local heuristic if `ANTHROPIC_API_KEY` is not set.
3. **Compare** - Prints a side-by-side table of per-axis means for two scored
   runs, plus the prompts whose scores changed the most.

## Setup

The harness imports `src.story_generator`, so run it from the project root.

Optional (for judge mode):

```bash
export ANTHROPIC_API_KEY=sk-ant-...
pip install "anthropic>=0.40"
```

Without that key/library, scoring falls back to the local heuristic and a
warning is logged. The heuristic is approximate and meant for quick local
iteration only - real comparisons should use the judge.

Judge mode cost: ~$0.01 per full 20-prompt run with the haiku model.

## Commands

```bash
# 1. Generate a fresh run of stories
python -m eval.run_eval
# -> eval/results/<utc-timestamp>.json

# Or pin the filename:
python -m eval.run_eval --output eval/results/run_A.json

# 2. Score a generation file (writes <name>.scored.json next to it)
python -m eval.run_eval --score eval/results/run_A.json
# -> eval/results/run_A.scored.json

# 3. Compare two scored runs
python -m eval.run_eval --compare \
    eval/results/run_A.scored.json \
    eval/results/run_B.scored.json
```

## Example workflow

You want to know if a tweaked prompt template in `src/story_generator.py`
actually helps:

```bash
# Baseline
python -m eval.run_eval --output eval/results/run_A.json
python -m eval.run_eval --score eval/results/run_A.json

# ... edit src/story_generator.py (e.g. change _create_prompt) ...

# Candidate
python -m eval.run_eval --output eval/results/run_B.json
python -m eval.run_eval --score eval/results/run_B.json

# See which axes moved
python -m eval.run_eval --compare \
    eval/results/run_A.scored.json \
    eval/results/run_B.scored.json
```

A positive `delta (B-A)` means B is better on that axis. The "Top per-prompt
changes" table points you at the prompts you should re-read by hand to sanity
check the numbers.

## Files

- `prompts.json` - 20 fixed eval prompts, each with `id`, `prompt`, `tags`.
- `run_eval.py` - The CLI (generate / score / compare).
- `results/` - Output JSON files. Git-ignored by default; only `.gitkeep` and
  `.gitignore` are tracked.

## Notes

- The judge-LLM rubric lives in `JUDGE_SYSTEM_PROMPT` inside `run_eval.py`. If
  you tighten the rubric, re-score both A and B before comparing - the compare
  table warns if the two runs were scored with different scorers, but it cannot
  tell if the rubric text drifted.
- The heuristic deliberately re-implements a tiny in-file unsafe-word list
  rather than importing from `src/safety.py`; that module may not exist yet or
  may change while other agents work on the codebase.
