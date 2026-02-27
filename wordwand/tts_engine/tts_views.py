import os
import re
import json
import time

import cv2
import nltk
from nltk.corpus import cmudict, words as english_words
from gtts import gTTS
from PyPDF2 import PdfReader

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
import pytesseract

from .models import TTSRequest

# ---------------------------------------------------------------------------
# NLTK setup — download once on first use
# ---------------------------------------------------------------------------
try:
    nltk.data.find('corpora/cmudict')
except LookupError:
    nltk.download('cmudict')

try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words')

_cmu_dict = cmudict.dict()
_english_words = set(english_words.words())

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SUPPORTED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tiff", "pdf", "txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

COMMON_WORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
    'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
    'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
    'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other',
    'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
    'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way',
    'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us',
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def split_into_syllables(word):
    """Return a hyphen-separated syllable breakdown for a word."""
    word = re.sub(r"[^\w]", "", word.lower().strip())
    if not word:
        return word

    if word in _cmu_dict:
        phonemes = _cmu_dict[word][0]
        syllables, current = [], []
        for phoneme in phonemes:
            current.append(phoneme.rstrip('012'))
            if phoneme[-1].isdigit():
                syllables.append(''.join(current))
                current = []
        if current:
            syllables.append(''.join(current))
        return '-'.join(syllables)

    # Fallback: simple vowel-boundary split
    vowels = 'aeiouy'
    syllables, current = [], []
    for i, char in enumerate(word):
        current.append(char)
        if char in vowels and i < len(word) - 1 and word[i + 1] not in vowels:
            syllables.append(''.join(current))
            current = []
    if current:
        syllables.append(''.join(current))
    return '-'.join(syllables) if len(syllables) > 1 else word


def is_hard(word):
    """Return True if a word is likely difficult for a child reader."""
    word = re.sub(r"[^\w]", "", word.lower().strip())
    if not word or len(word) <= 2 or word in COMMON_WORDS:
        return False
    vowels = 'aeiouy'
    vowel_count = sum(1 for c in word if c in vowels)
    return len(word) >= 6 or vowel_count >= 3 or (len(word) >= 4 and word not in COMMON_WORDS)


def extract_text_from_file(file_path, file_ext):
    """Extract plain text from an uploaded file."""
    text = ""

    if file_ext in {"png", "jpg", "jpeg", "bmp", "tiff"}:
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
        img = cv2.imread(file_path)
        if img is None:
            raise ValueError("Could not read image file.")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)

    elif file_ext == "pdf":
        pdf = PdfReader(file_path)
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    elif file_ext == "txt":
        for encoding in ("utf-8", "latin-1"):
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    text = f.read()
                break
            except UnicodeDecodeError:
                continue

    return text.strip()


def clean_text(text):
    """Normalise whitespace and punctuation spacing."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    text = re.sub(r'([.,!?;:])(\w)', r'\1 \2', text)
    return text.strip()


# ---------------------------------------------------------------------------
# View
# ---------------------------------------------------------------------------

@login_required
def reader(request):
    context = {
        "text": "",
        "error": "",
        "audio_url": "",
        "hard_words": json.dumps([]),
        "unique_hard_words": json.dumps([]),
        "syllables": json.dumps({}),
    }

    if request.method != "POST":
        return render(request, "reader.html", context)

    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        context["error"] = "Please select a file."
        return render(request, "reader.html", context)

    if uploaded_file.size > MAX_FILE_SIZE:
        context["error"] = "File too large. Maximum size is 10 MB."
        return render(request, "reader.html", context)

    file_name = uploaded_file.name
    file_ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""

    if file_ext not in SUPPORTED_EXTENSIONS:
        context["error"] = f"Unsupported file type '.{file_ext}'. Allowed: {', '.join(sorted(SUPPORTED_EXTENSIONS))}."
        return render(request, "reader.html", context)

    media_dir = settings.MEDIA_ROOT
    os.makedirs(media_dir, exist_ok=True)
    # Use a random suffix to avoid filename collisions
    safe_name = f"{os.urandom(8).hex()}_{file_name}"
    file_path = os.path.join(media_dir, safe_name)

    try:
        start_time = time.time()

        with open(file_path, "wb+") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        text = extract_text_from_file(file_path, file_ext)

        if not text or len(text.strip()) < 10:
            context["error"] = "No readable text found in the file."
            return render(request, "reader.html", context)

        text = clean_text(text)

        # Generate TTS audio
        tts = gTTS(text, lang='en')
        audio_filename = f"speech_{os.urandom(4).hex()}.mp3"
        audio_path = os.path.join(media_dir, "tts_audio", audio_filename)
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        tts.save(audio_path)
        audio_url = f"{settings.MEDIA_URL}tts_audio/{audio_filename}"

        # Hard-word detection
        words_raw = re.findall(r"\b[\w']+\b", text)
        hard_words = [w.lower() for w in words_raw if is_hard(re.sub(r"[^\w]", "", w.lower()))]
        unique_hard_words = sorted(set(hard_words))
        word_syllables = {w: split_into_syllables(w) for w in unique_hard_words}

        processing_time = round(time.time() - start_time, 2)

        TTSRequest.objects.create(
            user=request.user,
            audio_file=f"tts_audio/{audio_filename}",
            extracted_text=text,
            hard_words=unique_hard_words,
            syllables=word_syllables,
            file_type=file_ext,
            processing_time=processing_time,
        )

        context.update({
            "text": text,
            "audio_url": audio_url,
            "hard_words": json.dumps(hard_words),
            "unique_hard_words": json.dumps(unique_hard_words),
            "syllables": json.dumps(word_syllables, ensure_ascii=False),
        })

    except Exception as e:
        context["error"] = f"Error processing file: {e}"

    finally:
        # Always clean up the temp upload
        if os.path.exists(file_path):
            os.remove(file_path)

    return render(request, "reader.html", context)
