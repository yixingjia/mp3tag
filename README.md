Note: Find some mp3s that are back to 20 years ago, find there are quite a few garbled texts. try to fix with exsiting tools but failed. so create this local tools to fix the issue.

# MP3 Tag Editor Web Application
A lightweight, web-based MP3 metadata editor built with Flask and FFmpeg for batch editing audio file tags through a simple browser interface.

# ✨ Features
**Web-Based Interface:** Edit MP3 tags directly in your browser

**Batch Processing:** View and edit multiple files from a directory

**Smart Encoding:** Automatic handling of various audio formats (MP2, MP3, etc.)

**Preservation of Audio Quality:** Uses FFmpeg's copy mode when possible, re-encodes only when necessary

**Multi-format Support:** Handles standard MP3 files and problematic MP2-encoded MP3 files

**Fallback Mechanisms:** Multiple strategies to ensure successful tag updates

# 🛠️ Requirements

## Core Dependencies
```
Python 3.8 or higher

Flask 2.3.3 or higher

FFmpeg 4.0 or higher (7.1 recommended)

FFprobe (usually included with FFmpeg)
```

# 📦 Installation
## 1. Clone/Download
```
bash
git clone https://github.com/yixingjia/mp3tag.git
cd mp3tag
```
## 2. Install Python Dependencies
```
bash
pip install flask
```
## 3. Install FFmpeg

macOS (using Homebrew):
```
bash
brew install ffmpeg
```

Ubuntu/Debian:
```
bash
sudo apt update
sudo apt install ffmpeg
```
Windows:
```
Download from ffmpeg.org and add to PATH.
```
## 4. Configuration
Edit app.py and set the music directory path:
```
python
MUSIC_DIR = "/Users/admin/Downloads/music/yuyin"  # Change this to your actual directory
```
# 🚀 Usage
## 1. Start the Application
```
bash
python app.py
```
## 2. Access the Web Interface
Open your browser and navigate to:
```
http://localhost:5002
```
## 3. Edit MP3 Tags
Browse the list of MP3 files in your configured directory

Click the "Edit" button next to any file

Modify the metadata fields:
```
Title

Artist

Album

Year

Genre
```
Click "Save Changes" to update the file

# 🔧 Technical Details
## How It Works
**File Scanning:** The app scans the configured directory for .mp3 files

**Metadata Reading:** Uses FFprobe to extract existing tags

**Tag Editing:** Presents a web form for editing metadata

**Smart Updating:** Implements multiple strategies for updating tags:

**Primary Method:** FFmpeg stream copy (preserves audio quality)

**Fallback Method:** Re-encodes cover images when necessary

**Advanced Fallback:** Re-encodes entire audio stream for problematic files


## Supported Metadata Fields
**title:** Song title

**artist:** Performer/artist name

**album:** Album name

**date:** Release year/date

**genre:** Music genre/category

## File Format Support
Standard MP3 files (ID3v1, ID3v2.3, ID3v2.4)

MP2-encoded MP3 files (automatic re-encoding)

Files with embedded album art

Files with various character encodings

# 🐛 Troubleshooting
## Common Issues & Solutions
1. "Directory does not exist" Error
Solution: Update MUSIC_DIR in app.py to point to an existing directory.

2. FFmpeg Command Failures
Solution:

Ensure FFmpeg is installed and in PATH

Check file permissions

3. Character Encoding Issues
Solution: The app handles UTF-8 encoding. For files with different encodings, FFmpeg will attempt to preserve them.

4. Port Already in Use
Solution: Change the port in the last line of app.py:
```
python
app.run(debug=True, port=5003)  # Change 5002 to another port
```
**Error Messages**
"保留内容修改失败，尝试降级修复方案...": The primary method failed, attempting fallback

"降级方案执行成功（已重新编码封面，音频无损）": Fallback succeeded with cover re-encoding

"检测到MP2编码的MP3文件，重新编码为标准MP3格式...": MP2-encoded file detected, re-encoding to MP3

# 📁 Project Structure

mp3-tag-editor/
├── app.py              # Main application file
└── README.md           # This documentation

# 🔒 Security Notes
This application runs locally on your machine

No authentication is implemented (not intended for public deployment)

File operations are limited to the configured directory

Always backup your files before batch editing

# 📄 License
This tool is provided as-is for personal use. Modify and distribute as needed.

# 🤝 Contributing
Feel free to:

Report issues with specific file formats

# Suggest new features

Submit pull requests for improvements

Share compatibility notes for different systems

# 📧 Support
For issues, questions, or suggestions:

Check the Troubleshooting section above

Ensure FFmpeg is properly installed

Verify file permissions in your music directory

Check the console output for detailed error messages
