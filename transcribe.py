#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import urllib.request

# Configuration
MODEL_NAME = "base.en" # 'base.en' is fast and highly accurate.
MODEL_FILENAME = f"ggml-{MODEL_NAME}.bin"
MODEL_DIR = os.path.expanduser("~/.cache/whisper-cpp")
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)
MODEL_URL = f"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/{MODEL_FILENAME}"

# Add common Mac ports paths to PATH env variable just in case
extra_paths = ["/opt/homebrew/bin", "/usr/local/bin"]
for path in extra_paths:
    if path not in os.environ["PATH"]:
        os.environ["PATH"] = f"{path}:{os.environ['PATH']}"

def check_dependencies():
    print("Checking dependencies...")
    ffmpeg_installed = shutil.which("ffmpeg") is not None
    
    # Check for whisper-cli (Homebrew name) or whisper-cpp
    whisper_bin = None
    if shutil.which("whisper-cli") is not None:
        whisper_bin = "whisper-cli"
    elif shutil.which("whisper-cpp") is not None:
        whisper_bin = "whisper-cpp"

    if not ffmpeg_installed or whisper_bin is None:
        print("\n[!] Missing Prerequisites:")
        if not ffmpeg_installed:
            print("    - ffmpeg is NOT installed.")
        if whisper_bin is None:
            print("    - whisper-cli (or whisper-cpp) is NOT installed.")
        print("\nPlease run the following command in your terminal to install them:")
        print("    brew install whisper-cpp ffmpeg\n")
        sys.exit(1)
    
    print(f"[✓] ffmpeg and {whisper_bin} are installed.")
    return whisper_bin

def download_model():
    if os.path.exists(MODEL_PATH):
        print(f"[✓] Whisper model already exists at: {MODEL_PATH}")
        return

    print(f"Whisper model not found at {MODEL_PATH}.")
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # Try using whisper-cpp-download-ggml-model if it exists in PATH
    downloader = shutil.which("whisper-cpp-download-ggml-model")
    if downloader:
        print(f"Downloading model '{MODEL_NAME}' using whisper-cpp-download-ggml-model...")
        try:
            subprocess.run([downloader, MODEL_NAME], check=True)
            if os.path.exists(MODEL_PATH):
                return
        except subprocess.CalledProcessError:
            print("Downloader script failed, falling back to direct download...")

    # Fallback to direct download
    print(f"Downloading {MODEL_FILENAME} from Hugging Face ({MODEL_URL})...")
    print("This may take a minute depending on your connection (approx. 148 MB)...")
    
    def report_progress(block_num, block_size, total_size):
        read_so_far = block_num * block_size
        if total_size > 0:
            percent = min(100, (read_so_far * 100) / total_size)
            sys.stdout.write(f"\rDownloading: {percent:.1f}% ({read_so_far / (1024*1024):.1f}MB / {total_size / (1024*1024):.1f}MB)")
            sys.stdout.flush()
        else:
            sys.stdout.write(f"\rDownloading: {read_so_far / (1024*1024):.1f}MB")
            sys.stdout.flush()

    try:
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH, report_progress)
        print("\n[✓] Download complete!")
    except Exception as e:
        print(f"\n[!] Failed to download model: {e}")
        print(f"Please manually download the model from {MODEL_URL}")
        print(f"and save it to: {MODEL_PATH}")
        sys.exit(1)

def find_input_videos():
    desktop_dir = "/Users/aashish/Desktop"
    files = [f for f in os.listdir(desktop_dir) if f.endswith(".mov") or f.endswith(".mp4")]
    # Return absolute paths of all found files
    return [os.path.join(desktop_dir, f) for f in files]

def main():
    whisper_bin = check_dependencies()
    download_model()
    
    videos = find_input_videos()
    if not videos:
        print("[!] No .mov or .mp4 files found on Desktop.")
        sys.exit(1)
        
    print(f"\nFound {len(videos)} video file(s) on Desktop.")
    
    for index, video_path in enumerate(videos, start=1):
        video_name = os.path.basename(video_path)
        print(f"\n[{index}/{len(videos)}] File: {video_name}")
        
        audio_path = os.path.splitext(video_path)[0] + "_audio.wav"
        output_txt = audio_path + ".txt"
        
        # Check if the output text file already exists
        if os.path.exists(output_txt):
            print(f"  [✓] Already transcribed. Output file exists: {os.path.basename(output_txt)}")
            continue
        
        print("  -> Step 1: Extracting 16kHz mono audio using ffmpeg...")
        ffmpeg_cmd = ["ffmpeg", "-y", "-i", video_path, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", audio_path]
        
        try:
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  [✓] Audio extracted: {os.path.basename(audio_path)}")
        except subprocess.CalledProcessError as e:
            print(f"  [!] ffmpeg failed with exit code {e.returncode} for {video_name}")
            continue
            
        print(f"  -> Step 2: Transcribing audio using {whisper_bin}...")
        whisper_cmd = [whisper_bin, "-m", MODEL_PATH, "-f", audio_path, "-otxt", "-pp"]
        
        try:
            subprocess.run(whisper_cmd, check=True)
            print(f"  [✓] Transcription complete! Output saved to: {os.path.basename(output_txt)}")
            
            # Clean up intermediate audio wav file to save space
            if os.path.exists(audio_path):
                os.remove(audio_path)
                print(f"  [✓] Cleaned up temporary audio file: {os.path.basename(audio_path)}")
                
        except subprocess.CalledProcessError as e:
            print(f"  [!] {whisper_bin} failed with exit code {e.returncode} for {video_name}")
            continue

    # Open the output text file of the last processed video if on macOS
    if sys.platform == "darwin" and videos:
        # Sort videos to open the newest one that was processed
        unprocessed_videos = [v for v in videos if not os.path.exists(os.path.splitext(v)[0] + "_audio.wav.txt")]
        if unprocessed_videos:
            last_processed = unprocessed_videos[-1]
        else:
            last_processed = videos[-1]
            
        last_output_txt = os.path.splitext(last_processed)[0] + "_audio.wav.txt"
        if os.path.exists(last_output_txt):
            subprocess.run(["open", last_output_txt])

if __name__ == "__main__":
    main()
