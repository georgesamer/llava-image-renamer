# llava-image-renamer
A Python-based utility that uses the **LLaVA** vision model (via **Ollama**) to describe images and rename them with descriptive, SEO-friendly filenames. 

Everything runs locally on your machine—no cloud APIs, no costs, and total privacy.

## ✨ Features
- **Local AI:** Uses LLaVA to "see" and describe your photos.
- **Privacy First:** No images are uploaded to the internet.
- **Smart Renaming:** Converts descriptions into clean, hyphenated filenames.
- **Duplicate Handling:** Automatically appends numbers (e.g., `_1`, `_2`) if a filename already exists.
- **Dry Run Mode:** Preview changes before applying them.

## 🚀 Getting Started

### Prerequisites
1. **Ollama:** Download and install from [ollama.com](https://ollama.com).
2. **LLaVA Model:** Run the following command in your terminal:
   ```bash
   ollama pull llava
   ```

# Python Requirements:
  ```bash
  pip install ollama
  ```

# Usage
1. **Rename all images in a folder:**
  ```bash
  python app.py --folder "C:/Users/Name/Pictures"
  ```
2. **Rename specific files:**
  ```bash
  python app.py --files photo.jpg image.png
  ```
3. **Preview changes (Dry Run):**
  ```bash
  python app.py --folder ./my_images --dry-run
  ```

# Configuration
You can adjust the MAX_FILENAME_LENGTH in app.py to change the maximum length of the generated names (default is 60 characters).
