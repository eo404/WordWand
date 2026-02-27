import nltk
from nltk.corpus import cmudict, words as english_words
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
import pytesseract
import cv2
import os
import re
import json
import time
from PyPDF2 import PdfReader
from gtts import gTTS
from .models import TTSRequest
from django.contrib.auth.decorators import login_required

# Download NLTK data if not already downloaded
try:
    nltk.data.find('corpora/cmudict')
except LookupError:
    nltk.download('cmudict')
    nltk.download('words')

d = cmudict.dict()
english = set(english_words.words())

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
    'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us'
}


def split_into_syllables(word):
    word = word.lower().strip()
    word = re.sub(r'[^\w\s]', '', word)

    if word in d:
        phonemes = d[word][0]
        syllables = []
        current = []

        for phoneme in phonemes:
            current.append(phoneme.rstrip('012'))
            if phoneme[-1].isdigit():
                syllables.append(''.join(current))
                current = []

        return '-'.join(syllables)

    vowels = 'aeiouy'
    syllables = []
    current = []

    for i, char in enumerate(word):
        current.append(char)
        if char in vowels and i < len(word) - 1:
            next_char = word[i + 1]
            if next_char not in vowels:
                syllables.append(''.join(current))
                current = []

    if current:
        syllables.append(''.join(current))

    return '-'.join(syllables) if len(syllables) > 1 else word


def is_hard(word):
    if not word:
        return False

    word = word.lower().strip()
    word = re.sub(r'[^\w\s]', '', word)

    if len(word) <= 2:
        return False

    if word in COMMON_WORDS:
        return False

    vowels = 'aeiouy'
    vowel_count = sum(1 for char in word if char in vowels)

    if len(word) >= 6:
        return True

    if vowel_count >= 3:
        return True

    if len(word) >= 4 and word not in COMMON_WORDS:
        return True

    return False


def extract_text_from_file(file_path, file_ext):
    text = ""

    if file_ext in ["png", "jpg", "jpeg", "bmp", "tiff"]:
        img = cv2.imread(file_path)
        if img is not None:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray)
        else:
            raise ValueError("Could not read image file")

    elif file_ext == "pdf":
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    elif file_ext == "txt":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                text = f.read()

    else:
        raise ValueError(f"Unsupported file type: {file_ext}")

    return text.strip()


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    text = re.sub(r'([.,!?;:])(\w)', r'\1 \2', text)
    return text.strip()


@login_required
def reader(request):
    text = ""
    error = ""
    audio_url = ""
    hard_words = []
    unique_hard_words = []
    word_syllables = {}

    if request.method == "POST" and request.FILES.get("file"):
        start_time = time.time()

        uploaded_file = request.FILES["file"]
        file_name = uploaded_file.name

        if uploaded_file.size > 10 * 1024 * 1024:
            error = "File size too large. Maximum size is 10MB."
            return render(request, "reader.html", {"error": error})

        media_dir = settings.MEDIA_ROOT
        os.makedirs(media_dir, exist_ok=True)

        file_path = os.path.join(media_dir, file_name)

        try:
            with open(file_path, "wb+") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            file_ext = file_name.split(".")[-1].lower()
            supported_extensions = ["png", "jpg",
                                    "jpeg", "bmp", "tiff", "pdf", "txt"]

            if file_ext not in supported_extensions:
                error = "Unsupported file type."
                os.remove(file_path)
                return render(request, "reader.html", {"error": error})

            text = extract_text_from_file(file_path, file_ext)

            if not text or len(text.strip()) < 10:
                error = "No readable text found."
                os.remove(file_path)
                return render(request, "reader.html", {"error": error})

            text = clean_text(text)

            # Generate audio
            tts = gTTS(text, lang='en')
            audio_filename = f"speech_{os.path.splitext(file_name)[0]}_{os.urandom(4).hex()}.mp3"
            audio_path = os.path.join(media_dir, audio_filename)
            tts.save(audio_path)
            audio_url = f"/media/{audio_filename}"

            words_with_case = re.findall(r'\b[\w\']+\b', text)
            words_lower = [w.lower() for w in words_with_case]

            for i, word in enumerate(words_lower):
                clean_word = re.sub(r'[^\w\s]', '', word)
                if len(clean_word) <= 2:
                    continue
                if is_hard(clean_word):
                    hard_words.append(words_with_case[i].lower())

            unique_hard_words = sorted(list(set(hard_words)))

            for word in unique_hard_words:
                word_syllables[word] = split_into_syllables(word)

            processing_time = round(time.time() - start_time, 2)

            # Save to database
            TTSRequest.objects.create(
                user=request.user,
                extracted_text=text,
                audio_file=f"tts_audio/{audio_filename}",
                hard_words=unique_hard_words,
                syllables=word_syllables,
                file_type=file_ext,
                processing_time=processing_time
            )

            os.remove(file_path)

        except Exception as e:
            error = f"Error processing file: {str(e)}"
            if os.path.exists(file_path):
                os.remove(file_path)

    elif request.method == "POST":
        error = "Please select a file."

    context = {
        "text": text,
        "error": error,
        "audio_url": audio_url,
        "hard_words": json.dumps(hard_words),
        "unique_hard_words": json.dumps(unique_hard_words),
        "syllables": json.dumps(word_syllables, ensure_ascii=False)
    }

    return render(request, "reader.html", context)
