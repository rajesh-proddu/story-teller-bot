# Architecture & Design

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│                Story Teller Bot System                  │
└─────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┬────────────────┐
        │                     │                     │                │
    ┌───▼───┐          ┌──────▼──────┐      ┌──────▼─────┐    ┌────▼────┐
    │ Audio │          │   Speech    │      │   Story    │    │  Audio  │
    │ Input │          │ Recognition │      │ Generation │    │ Output  │
    │Handler│          │             │      │            │    │Handler  │
    └───┬───┘          └──────┬──────┘      └──────┬─────┘    └────┬────┘
        │                     │                     │              │
        │ PCM Audio           │ Text                │ Story         │ Speech
        │ (numpy array)       │ (Transcript)        │ Text          │ Audio/TTS
        └─────────────────────┼─────────────────────┴──────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Story Teller Bot │
                    │   (Orchestrator)  │
                    └───────────────────┘
```

## Component Architecture

### 1. Audio Handler (`src/audio_handler.py`)

#### AudioInputHandler
- **Responsibility**: Capture audio from microphone
- **Key Methods**:
  - `record_audio()`: Records audio for specified duration
  - `save_audio()`: Saves recorded audio to WAV file
  - `stop_recording()`: Stops ongoing recording

**Flow**:
```
User speaks → sounddevice records → numpy array → WAV file
```

#### AudioOutputHandler
- **Responsibility**: Play audio and text-to-speech
- **Key Methods**:
  - `speak()`: Convert text to speech and play
  - `play_audio()`: Play existing audio file
  - `pause_playback()`: Pause playback
  - `stop_playback()`: Stop playback

**Flow**:
```
Text → pyttsx3 (TTS) → Audio file → sounddevice plays → User hears
```

### 2. Speech Recognition (`src/speech_recognizer.py`)

#### SpeechRecognizer
- **Model**: OpenAI Whisper
- **Responsibility**: Convert audio to text
- **Key Methods**:
  - `transcribe()`: Transcribe audio to text
  - `transcribe_from_file()`: Transcribe from file

**Supported Models**:
- `tiny`: 39M parameters, fastest
- `base`: 140M parameters (default)
- `small`: 244M parameters
- `medium`: 769M parameters
- `large`: 1550M parameters

**Flow**:
```
Audio file → Whisper model → Tokenization → ML Model → Text
```

### 3. Story Generation (`src/story_generator.py`)

#### StoryGenerator
- **Model**: Transformers (GPT-2)
- **Responsibility**: Generate creative stories
- **Key Methods**:
  - `extract_objects()`: Parse user input for story elements
  - `generate_story()`: Generate story with given objects
  - `generate_story_from_input()`: End-to-end story generation

**Pipeline**:
```
User Input → Extract Objects → Create Prompt → GPT-2 Model → Story Text
```

**Example**:
```
Input: "I want a story with a king and lion"
Objects: ["king", "lion"]
Prompt: "Once upon a time, in a magical kingdom with king, lion..."
Output: Full story text
```

### 4. Main Bot (`src/bot.py`)

#### StoryTellerBot
- **Responsibility**: Orchestrate all components
- **State Machine**:
  - `IDLE`: Waiting for input
  - `LISTENING`: Recording audio
  - `PROCESSING`: Transcribing and generating
  - `SPEAKING`: Playing audio
  - `PAUSED`: Playback paused
  - `STOPPED`: Operation stopped

**Workflow**:
```
START (IDLE)
  ↓
[Display Menu]
  ↓
User selects mode
  ├─→ Audio Input Mode
  │    ↓
  │   [LISTENING] - Record audio
  │    ↓
  │   [PROCESSING] - Transcribe speech
  │    ↓
  │   [Get user text]
  │    ↓
  │   └─→ Generate Story
  │
  └─→ Text Input Mode
       ↓
      [Get user text]
       ↓
       └─→ Generate Story
             ↓
            [SPEAKING] - Play audio
             ↓
            [Options: Pause/Stop]
             ↓
            [IDLE] - Done
```

## Data Flow

### Audio Input Flow

```
┌──────────────────┐
│  Microphone      │
└────────┬─────────┘
         │ Audio Signal
         ▼
┌──────────────────────┐
│ sounddevice.rec()    │ Recording
├──────────────────────┤
│ Converts to PCM      │
└────────┬─────────────┘
         │ numpy.ndarray
         ▼
┌──────────────────────┐
│ soundfile.write()    │ Storage
├──────────────────────┤
│ Creates WAV file     │
└────────┬─────────────┘
         │ WAV file
         ▼
┌──────────────────────┐
│ SpeechRecognizer     │ Processing
└──────────────────────┘
```

### Text Generation Flow

```
┌──────────────────┐
│ Transcribed Text │
└────────┬─────────┘
         │
         ▼
┌────────────────────────┐
│ extract_objects()      │
├────────────────────────┤
│ NLP parsing to find    │
│ nouns (objects/chars)  │
└────────┬───────────────┘
         │ List of objects
         ▼
┌────────────────────────┐
│ _create_prompt()       │
├────────────────────────┤
│ Generate template      │
│ with objects           │
└────────┬───────────────┘
         │ Prompt text
         ▼
┌────────────────────────┐
│ Transformers Pipeline  │
├────────────────────────┤
│ GPT-2 Model            │
│ Text Generation        │
└────────┬───────────────┘
         │ Generated text
         ▼
┌────────────────────────┐
│ _clean_story()         │
├────────────────────────┤
│ Remove artifacts       │
│ Format paragraphs      │
└────────┬───────────────┘
         │ Clean story text
         ▼
┌────────────────────────┐
│ Story Ready for TTS    │
└────────────────────────┘
```

### Audio Output Flow

```
┌──────────────────┐
│ Story Text       │
└────────┬─────────┘
         │
         ▼
┌────────────────────────┐
│ pyttsx3 TTS Engine     │
├────────────────────────┤
│ Text → Phonemes        │
│ Prosody synthesis      │
│ Audio generation       │
└────────┬───────────────┘
         │ Audio data
         ▼
┌────────────────────────┐
│ Save to WAV file       │
│ (Optional storage)     │
└────────┬───────────────┘
         │ WAV file
         ▼
┌────────────────────────┐
│ sounddevice.play()     │
├────────────────────────┤
│ Audio playback         │
└────────┬───────────────┘
         │ Audio signals
         ▼
┌──────────────────┐
│ Speaker/Headset  │
└──────────────────┘
```

## Configuration Architecture

```
config/
├── settings.py
│   └── Settings (Pydantic BaseSettings)
│       ├── Paths (logs, models, audio)
│       ├── Audio Config (sample_rate, duration)
│       ├── Model Config (whisper, gpt2)
│       ├── Generation Config (temperature, length)
│       └── Logging Config
```

### Configuration Priority

```
1. Environment Variables (.env) - Highest
2. .env file values
3. Hardcoded defaults - Lowest
```

## Deployment Architecture

### Local Machine
```
Virtual Environment
├── Python Interpreter
├── Dependencies
├── Models Cache
└── Application Code
```

### Systemd Service
```
/etc/systemd/system/
└── story-teller-bot.service
    ├── Auto-start on boot
    ├── Auto-restart on failure
    ├── Isolated environment
    └── Logging to journalctl
```

### Docker Container
```
Docker Image
├── Python 3.11 base
├── System dependencies
├── Python packages
├── Application code
└── Virtual environment

Container Instance
├── Isolated environment
├── Volume mounts
├── Device mapping (/dev/snd)
└── Network isolation
```

### Docker Compose
```
docker-compose.yml
├── Story Teller Bot service
├── Volumes for persistence
├── Device mapping for audio
└── Health checks
```

## Model Architecture

### Whisper (Speech Recognition)

```
Audio Input (16 kHz)
        ↓
┌───────────────────┐
│ Mel-Spectrogram   │ (Time-frequency analysis)
│ Computation       │
└───────────┬───────┘
            ↓
    ┌───────────────┐
    │ Encoder       │ (Extract features)
    │ (Transformer) │
    └───────┬───────┘
            ↓
    ┌───────────────┐
    │ Decoder       │ (Generate tokens)
    │ (Transformer) │
    └───────┬───────┘
            ↓
┌───────────────────┐
│ Token Prediction  │
│ (Softmax)         │
└───────────┬───────┘
            ↓
┌───────────────────┐
│ Transcribed Text  │
└───────────────────┘
```

### GPT-2 (Story Generation)

```
Prompt Text
    ↓
┌──────────────────┐
│ Tokenization     │ (String → Token IDs)
└────────┬─────────┘
         ↓
┌──────────────────────┐
│ Token Embedding      │ (1D → 768D vectors)
└────────┬─────────────┘
         ↓
┌──────────────────────┐
│ Transformer Blocks   │ (12 layers)
│ - Attention layers   │
│ - Feed-forward       │
│ - Layer normalization│
└────────┬─────────────┘
         ↓
┌──────────────────────┐
│ Output Projection    │ (768D → Vocab size)
└────────┬─────────────┘
         ↓
┌──────────────────────┐
│ Sampling/Decoding    │ (Temperature, top-p)
│ Select next token    │
└────────┬─────────────┘
         ↓
┌──────────────────────┐
│ Repeat until         │ (Stop condition or
│ sequence complete    │  max length)
└────────┬─────────────┘
         ↓
┌──────────────────────┐
│ De-tokenization      │ (Token IDs → String)
└────────┬─────────────┘
         ↓
┌──────────────────────┐
│ Generated Story      │
└──────────────────────┘
```

## Performance Considerations

### Memory Usage
- Whisper base: ~140MB
- GPT-2: ~540MB
- pyttsx3: ~50MB
- Total: ~800MB + OS/Python overhead

### Computation Time
- Audio recording: Real-time
- Transcription: 10-30 seconds per minute of audio
- Story generation: 5-15 seconds for 500 words
- TTS: 5-20 seconds per 500 words

### Optimization Strategies
1. **Model Quantization**: Use smaller precision (int8)
2. **Model Distillation**: Use smaller models (tiny, distilgpt2)
3. **Caching**: Cache models locally
4. **Batching**: Process multiple requests together
5. **Device**: GPU acceleration (if available)

## Security Considerations

### Data Privacy
- All processing local (no cloud)
- Audio files stored locally
- No external API calls
- User control over data

### Access Control
- Docker non-root user
- File permissions
- Systemd service limitations
- Environment variable isolation

### Model Safety
- Using established models (OpenAI Whisper, GPT-2)
- Input validation
- Error handling
- Logging for audit trail

## Testing Architecture

```
Tests/
├── Unit Tests
│   ├── test_audio_handler.py
│   ├── test_speech_recognizer.py
│   ├── test_story_generator.py
│   └── test_bot.py
├── Integration Tests (future)
└── E2E Tests (future)
```

### Test Coverage Target: 80%+

## Future Enhancements

1. **Multi-language Support**
   - Add language detection
   - Support multiple Whisper models
   - Translate stories

2. **Advanced Story Generation**
   - Larger models (GPT-3, GPT-J)
   - Fine-tuning on stories
   - Story length control

3. **Web Interface**
   - REST API
   - Web UI
   - Real-time streaming

4. **Streaming Audio**
   - Real-time transcription
   - Streaming generation
   - Streaming playback

5. **Persistence**
   - Database for stories
   - User preferences
   - Story history

6. **Performance**
   - Model quantization
   - GPU support
   - Hardware acceleration

7. **Accessibility**
   - Multiple input methods
   - Output formats
   - Customization options
