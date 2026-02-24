#!/usr/bin/env python3
"""
Simple Vietnamese TTS script using Piper.
Allows users to enter text and generate WAV files.
"""

import sys
import wave
from pathlib import Path
from piper import PiperVoice
from predict import Predictor


def main():
    """Main function to run TTS."""
    print("Vietnamese TTS using Piper")
    print("=" * 50)
    
    # Initialize predictor (loads models and normalization)
    print("Loading models...")
    predictor = Predictor()
    predictor.setup()
    print("Models loaded successfully!\n")
    
    # Get voice model choice
    print("Available voices:")
    print("1. ngochuyen")
    print("2. tranthanh")
    voice_choice = input("\nSelect voice (1 or 2, default: 1): ").strip()
    
    if voice_choice == "2":
        model = "tranthanh"
    else:
        model = "ngochuyen"
    
    print(f"\nUsing voice: {model}\n")
    
    # Get text input
    print("Enter text to synthesize (or 'quit' to exit):")
    print("-" * 50)
    
    while True:
        text = input("\nText: ").strip()
        
        if text.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not text:
            print("Please enter some text.")
            continue
        
        # Get output filename
        output_file = input("Output filename (default: output.wav): ").strip()
        if not output_file:
            output_file = "output.wav"
        
        if not output_file.endswith('.wav'):
            output_file += '.wav'
        
        try:
            print(f"\nProcessing text...")
            
            # Normalize text
            normalized_text = predictor._normalize_text(text)
            print(f"Normalized text: {normalized_text}")
            
            # Get voice
            voice = predictor._get_voice(model)
            
            # Synthesize to WAV file
            print("Synthesizing speech...")
            with wave.open(output_file, "wb") as wav_file:
                voice.synthesize_wav(normalized_text, wav_file)
            
            print(f"✓ Audio saved to: {output_file}\n")
            
        except Exception as e:
            print(f"✗ Error: {e}\n")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
        sys.exit(0)

