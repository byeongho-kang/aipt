import os
from openai import OpenAI
from dotenv import load_dotenv
import glob

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

def transcribe_audio(audio_path):
    """
    Transcribe an audio file using OpenAI's Whisper API
    """
    try:
        with open(audio_path, "rb") as audio_file:
            # Transcribe the audio file
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ko"  # Specify Korean language
            )
            
            # Create output filename
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            output_path = os.path.join("texts", f"{base_name}.txt")
            
            # Save the transcription
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(transcript.text)
            
            print(f"Transcription saved to {output_path}")
            return transcript.text
            
    except Exception as e:
        print(f"Error transcribing {audio_path}: {str(e)}")
        return None

def main():
    # Create texts directory if it doesn't exist
    if not os.path.exists("texts"):
        os.makedirs("texts")
    
    # Get all wav files in the current directory
    wav_files = glob.glob("*.wav")
    
    if not wav_files:
        print("No WAV files found in the current directory")
        return
    
    print(f"Found {len(wav_files)} WAV files")
    
    # Process each WAV file
    for wav_file in wav_files:
        print(f"\nProcessing {wav_file}...")
        transcribe_audio(wav_file)

if __name__ == "__main__":
    main()
