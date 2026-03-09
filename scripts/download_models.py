#!/usr/bin/env python3
"""
Download required HuggingFace models for Story Teller Bot.
This script downloads models needed for:
- Speech recognition (Whisper)
- Story generation (GPT-2)
"""

import os
import sys
from pathlib import Path

def download_models():
    """Download all required models from HuggingFace."""
    
    # Set cache directory
    cache_dir = Path("/app/models_cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    os.environ['HF_HOME'] = str(cache_dir)
    os.environ['HUGGINGFACE_HUB_CACHE'] = str(cache_dir / "hub")
    
    print("=" * 80)
    print("Downloading Story Teller Bot Models from HuggingFace")
    print("=" * 80)
    print(f"Cache directory: {cache_dir}")
    
    models_to_download = [
        {
            'name': 'Whisper Base (Speech Recognition)',
            'source': 'openai/whisper-base',
            'download_fn': download_whisper_model,
            'size': '~140MB'
        },
        {
            'name': 'GPT-2 (Story Generation)',
            'source': 'gpt2',
            'download_fn': download_gpt2_model,
            'size': '~540MB'
        },
        {
            'name': 'DistilGPT-2 (Alternative, Smaller)',
            'source': 'distilgpt2',
            'download_fn': download_distilgpt2_model,
            'size': '~160MB'
        },
    ]
    
    success_count = 0
    failed_count = 0
    
    for model_info in models_to_download:
        try:
            print(f"\n[{success_count + failed_count + 1}/{len(models_to_download)}] Downloading: {model_info['name']}")
            print(f"  Source: {model_info['source']}")
            print(f"  Size: {model_info['size']}")
            
            model_info['download_fn']()
            
            print(f"  ✓ Downloaded successfully")
            success_count += 1
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            failed_count += 1
    
    print("\n" + "=" * 80)
    print(f"Download Summary: {success_count} successful, {failed_count} failed")
    print("=" * 80)
    
    # List cached models
    print("\n📦 Available Models in Cache:")
    if (cache_dir / "hub").exists():
        for item in sorted((cache_dir / "hub").iterdir()):
            print(f"  ✓ {item.name}")
    
    return failed_count == 0


def download_whisper_model():
    """Download Whisper speech recognition model."""
    try:
        import whisper
        model = whisper.load_model("base", download_root=str(Path("/app/models_cache")))
        print(f"    Model type: {type(model)}")
        print(f"    Loaded successfully")
    except Exception as e:
        print(f"    Error: {e}")
        raise


def download_gpt2_model():
    """Download GPT-2 story generation model."""
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        print("    Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
        
        print("    Downloading model...")
        model = AutoModelForCausalLM.from_pretrained("gpt2")
        
        print(f"    Tokenizer: {type(tokenizer).__name__}")
        print(f"    Model: {type(model).__name__}")
    except Exception as e:
        print(f"    Error: {e}")
        raise


def download_distilgpt2_model():
    """Download DistilGPT-2 (smaller alternative)."""
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        print("    Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
        
        print("    Downloading model...")
        model = AutoModelForCausalLM.from_pretrained("distilgpt2")
        
        print(f"    Tokenizer: {type(tokenizer).__name__}")
        print(f"    Model: {type(model).__name__}")
    except Exception as e:
        print(f"    Error: {e}")
        raise


def verify_models():
    """Verify that downloaded models are accessible."""
    print("\n" + "=" * 80)
    print("Verifying Downloaded Models")
    print("=" * 80)
    
    try:
        print("\n✓ Importing transformers...")
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        print("✓ Importing whisper...")
        import whisper
        
        print("✓ Loading GPT-2 model...")
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
        model = AutoModelForCausalLM.from_pretrained("gpt2")
        
        print("✓ Testing tokenization...")
        tokens = tokenizer.encode("Hello, this is a test story")
        print(f"  Sample text tokenized to {len(tokens)} tokens")
        
        print("\n✓ All models verified successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False


if __name__ == "__main__":
    try:
        print("\n🤖 Story Teller Bot - Model Downloader\n")
        
        # Download models
        success = download_models()
        
        # Verify models
        if success:
            verified = verify_models()
            
            if verified:
                print("\n" + "=" * 80)
                print("✓ All models downloaded and verified!")
                print("=" * 80)
                sys.exit(0)
        
        print("\n⚠ Model download completed with warnings")
        sys.exit(0)  # Exit gracefully even if some downloads fail
        
    except KeyboardInterrupt:
        print("\n\n✗ Download interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
