# ── Word Builder words ───────────────────────────────
from gtts import gTTS
import os

word_builder_words = [
    'cat', 'dog', 'sun', 'hat', 'big', 'map', 'run', 'top',
    'jump', 'frog', 'slip', 'clap', 'plant',
    'brush', 'chest', 'think', 'shrimp',
    'splash', 'strong', 'flight'
]

os.makedirs('media/words/audio', exist_ok=True)
for word in word_builder_words:
    tts = gTTS(word, lang='en')
    tts.save(f'media/words/audio/{word}.mp3')
    print(f'✅ word: {word}.mp3')
