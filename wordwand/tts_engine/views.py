import nltk
from nltk.corpus import cmudict, words as english_words
from django.shortcuts import render
import pytesseract
import cv2
import os
import re
from django.conf import settings
from PyPDF2 import PdfReader
from gtts import gTTS
import json

# Download NLTK data if not already downloaded
try:
    nltk.data.find('corpora/cmudict')
except LookupError:
    nltk.download('cmudict')
    nltk.download('words')

# Load dictionaries
d = cmudict.dict()
english = set(english_words.words())

# Common English words (top 500 most frequent)
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
    """
    Split a word into syllables for better readability
    Example: 'unbelievable' -> 'un-be-liev-a-ble'
    """
    word = word.lower().strip()

    # Remove punctuation
    word = re.sub(r'[^\w\s]', '', word)

    # Check if word is in CMU dictionary
    if word in d:
        # Get phonetic representation
        phonemes = d[word][0]

        # Split by syllables (phonemes ending with digits)
        syllables = []
        current_syllable = []

        for phoneme in phonemes:
            current_syllable.append(phoneme.rstrip('012'))
            if phoneme[-1].isdigit():  # Syllable boundary
                syllables.append(''.join(current_syllable))
                current_syllable = []

        # Join with hyphens
        return '-'.join(syllables)

    # Fallback: Use simple syllable splitting rules
    vowels = 'aeiouy'

    # Common prefixes and suffixes
    prefixes = ['un', 're', 'dis', 'mis', 'pre',
                'pro', 'con', 'com', 'per', 'sub', 'trans']
    suffixes = ['able', 'ible', 'ment', 'tion', 'sion', 'ence',
                'ance', 'ness', 'less', 'ful', 'est', 'ing', 'ed', 'er']

    # Try to split by common morphemes first
    for prefix in prefixes:
        if word.startswith(prefix) and len(word) > len(prefix) + 2:
            return f"{prefix}-{split_into_syllables(word[len(prefix):])}"

    for suffix in suffixes:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return f"{split_into_syllables(word[:-len(suffix)])}-{suffix}"

    # Simple vowel-based splitting (conservative)
    syllables = []
    current_syllable = []
    vowel_found = False

    for i, char in enumerate(word):
        current_syllable.append(char)

        if char in vowels:
            vowel_found = True

        # Syllable boundaries (simplified rules)
        if i < len(word) - 1:
            next_char = word[i + 1]

            # Rule 1: VC-CV pattern (vowel-consonant, consonant-vowel)
            if (char in vowels and next_char not in vowels and
                    i + 2 < len(word) and word[i + 2] not in vowels):
                syllables.append(''.join(current_syllable))
                current_syllable = []
                vowel_found = False

            # Rule 2: V-CV pattern (vowel, consonant-vowel)
            elif char in vowels and next_char not in vowels and vowel_found:
                if i + 2 < len(word) and word[i + 2] in vowels:
                    syllables.append(''.join(current_syllable))
                    current_syllable = []
                    vowel_found = False

    # Add remaining letters
    if current_syllable:
        syllables.append(''.join(current_syllable))

    # Ensure we don't have empty syllables
    syllables = [s for s in syllables if s]

    # Join with hyphens
    if len(syllables) > 1:
        return '-'.join(syllables)
    else:
        return word


def is_hard(word):
    """
    Simple hard word detection for dyslexic children:
    1. Words with 5+ letters are usually harder
    2. Words not in common vocabulary
    3. Multi-syllable words
    """
    if not word:
        return False

    word = word.lower().strip()
    word = re.sub(r'[^\w\s]', '', word)

    # Skip very short words
    if len(word) <= 2:
        return False

    # Skip very common words
    if word in COMMON_WORDS:
        return False

    # Check syllable count (simplified)
    vowels = 'aeiouy'
    vowel_count = sum(1 for char in word if char in vowels)

    # Rule 1: Long words (6+ letters)
    if len(word) >= 6:
        return True

    # Rule 2: Words with 3+ vowel sounds (likely multi-syllable)
    if vowel_count >= 3:
        return True

    # Rule 3: Medium words that aren't common
    if len(word) >= 4 and word not in COMMON_WORDS:
        return True

    return False


def extract_text_from_file(file_path, file_ext):
    """
    Extract text from different file formats
    """
    text = ""

    try:
        # Image OCR
        if file_ext in ["png", "jpg", "jpeg", "bmp", "tiff"]:
            img = cv2.imread(file_path)
            if img is not None:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string(gray)
            else:
                raise ValueError("Could not read image file")

        # PDF
        elif file_ext == "pdf":
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        # TXT
        elif file_ext == "txt":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            except UnicodeDecodeError:
                with open(file_path, "r", encoding="latin-1") as f:
                    text = f.read()

        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

    except Exception as e:
        raise Exception(
            f"Error extracting text from {file_ext.upper()} file: {str(e)}")

    return text.strip()


def clean_text(text):
    """
    Clean and normalize text
    """
    if not text:
        return ""

    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    text = re.sub(r'([.,!?;:])(\w)', r'\1 \2', text)

    return text.strip()


def reader(request):
    text = ""
    error = ""
    audio_url = ""
    hard_words = []
    unique_hard_words = []
    word_syllables = {}  # Changed from phonetics to syllables

    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        file_name = uploaded_file.name

        # Validate file size
        if uploaded_file.size > 10 * 1024 * 1024:
            error = "File size too large. Maximum size is 10MB."
            return render(request, "reader.html", {"error": error})

        # Create media directory
        media_dir = settings.MEDIA_ROOT
        os.makedirs(media_dir, exist_ok=True)

        # Save uploaded file
        file_path = os.path.join(media_dir, file_name)

        try:
            with open(file_path, "wb+") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            # Get file extension
            file_ext = file_name.split(".")[-1].lower()

            # Validate file extension
            supported_extensions = ["png", "jpg",
                                    "jpeg", "bmp", "tiff", "pdf", "txt"]
            if file_ext not in supported_extensions:
                error = f"Unsupported file type. Supported types: {', '.join(supported_extensions)}"
                os.remove(file_path)
                return render(request, "reader.html", {"error": error})

            # Extract text
            text = extract_text_from_file(file_path, file_ext)

            if not text or len(text.strip()) < 10:
                error = "No readable text found. Please try a different file."
                os.remove(file_path)
                return render(request, "reader.html", {"error": error})

            # Clean text
            text = clean_text(text)

            # Generate audio
            try:
                tts = gTTS(text, lang='en')
                audio_filename = f"speech_{os.path.splitext(file_name)[0]}_{os.urandom(4).hex()}.mp3"
                audio_path = os.path.join(media_dir, audio_filename)
                tts.save(audio_path)
                audio_url = f"/media/{audio_filename}"

                # Clean up old audio files
                audio_files = [f for f in os.listdir(media_dir) if f.startswith(
                    'speech_') and f.endswith('.mp3')]
                audio_files.sort(key=lambda x: os.path.getctime(
                    os.path.join(media_dir, x)))
                for old_file in audio_files[:-5]:
                    try:
                        os.remove(os.path.join(media_dir, old_file))
                    except:
                        pass

            except Exception as e:
                print(f"Audio generation error: {str(e)}")

            # Extract words
            words_with_case = re.findall(r'\b[\w\']+\b', text)
            words_lower = [w.lower() for w in words_with_case]

            # Find hard words
            hard_words = []
            for i, word in enumerate(words_lower):
                clean_word = re.sub(r'[^\w\s]', '', word)

                if len(clean_word) <= 2:
                    continue

                if is_hard(clean_word):
                    hard_words.append(words_with_case[i].lower())

            # Get unique hard words
            unique_hard_words = list(set(hard_words))
            unique_hard_words.sort()

            # Split each hard word into syllables
            word_syllables = {}
            for word in unique_hard_words:
                syllables = split_into_syllables(word)
                word_syllables[word] = syllables

            # Clean up
            try:
                os.remove(file_path)
            except:
                pass

        except Exception as e:
            error = f"Error processing file: {str(e)}"
            try:
                if 'file_path' in locals() and os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass

    elif request.method == "POST":
        error = "Please select a file to upload."

    # Prepare context
    context = {
        "text": text,
        "error": error,
        "audio_url": audio_url,
        "hard_words": json.dumps(hard_words),
        "unique_hard_words": json.dumps(unique_hard_words),
        # Changed from phonetics
        "syllables": json.dumps(word_syllables, ensure_ascii=False)
    }

    return render(request, "reader.html", context)
