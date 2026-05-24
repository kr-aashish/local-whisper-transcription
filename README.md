# local-whisper-transcription 🎙️

A lightweight, C/C++ local speech-to-text pipeline optimized for **Apple Silicon Macs (M1/M2/M3)**. Powered by Georgi Gerganov's **[`whisper.cpp`](https://github.com/ggml-org/whisper.cpp)** and **`ffmpeg`**, it transcribes audio locally on your Mac's GPU via Metal acceleration with **zero data sent to the cloud, $0 cost, and zero context window limits**.

## 🚀 Speed Performance (Tested on M1 Pro Mac)
* **Video Duration:** `3 hours, 16 minutes` (11,795 seconds)
* **File Size:** `3.6 GB`
* **Local Processing Time:** **`103.4 seconds`** (~1.7 minutes)
* **Efficiency:** **`114x faster than real-time`**!

---

## 🛠️ Prerequisites & Installation

To run this pipeline, you need **Homebrew** installed.

1. **Install ffmpeg & whisper-cpp:**
   ```bash
   brew install whisper-cpp ffmpeg
   ```
   *Note: Homebrew installs `whisper-cpp` and creates symlinks for `whisper-cli` in `/opt/homebrew/bin/`.*

---

## ⚙️ Automated Workflow Script

The repo contains **`transcribe.py`**, a script that automates the entire end-to-end flow for any video files located in a target directory (defaults to your Desktop).

### What `transcribe.py` Does:
1. **Scans for Videos:** Looks for `.mov` and `.mp4` files.
2. **Skips Already Processed Files:** Prevents duplicate transcription if the transcript output already exists.
3. **Extracts Audio:** Converts video to `16kHz`, `mono`, `16-bit PCM WAV` using `ffmpeg` (the exact format required by Whisper).
4. **Downloads the Model:** Automatically fetches the `ggml-base.en.bin` model (approx. 148 MB) from Hugging Face if not found in cache.
5. **Transcribes Local GPU Acceleration:** Invokes the `whisper-cli` binary utilizing **Metal** on Apple Silicon to perform lightning-fast local transcription.
6. **Cleans Up:** Deletes temporary `.wav` files once the transcription is written to `.txt`.

### How to Run:
```bash
python3 transcribe.py
```

---

## 🗂️ Manual Commands (Standard Method)

If you wish to run the commands manually on a single file:

1. **Convert the Video to Audio:**
   ```bash
   ffmpeg -y -i "recording.mov" -ar 16000 -ac 1 -c:a pcm_s16le audio.wav
   ```
2. **Download the model:**
   ```bash
   whisper-cpp-download-ggml-model base.en
   ```
3. **Transcribe:**
   ```bash
   whisper-cli -m ~/.cache/whisper-cpp/ggml-base.en.bin -f audio.wav -otxt
   ```

---

## 🧠 SDE Prompt for Masterclass Notes

Once you have the text file transcript, copy-paste it into an LLM (Claude, ChatGPT, Gemini) using this prompt to generate technical summaries:

```text
I have a raw transcript of a backend engineering masterclass. Please extract:
1. Architecture Diagrams: Describe any system designs mentioned in Mermaid.js format.
2. The 'Aha!' Moments: Key insights that differentiate this from basic tutorials.
3. Actionable Code: List any specific implementation logic discussed.
```

---

## 📂 Repository Contents
* **`transcribe.py`**: The optimized Python runner.
* **`whisper_transcription_guide.md`**: Complete step-by-step workflow guide.
* **`README.md`**: This guide.
