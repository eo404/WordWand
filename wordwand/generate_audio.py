from gtts import gTTS
import os

# ── Listen & Type words ──────────────────────────
listen_words = [
    'cat', 'dog', 'sun', 'hat', 'red', 'big', 'cup', 'pen',
    'frog', 'clap', 'step', 'slip', 'brush', 'chest', 'think', 'plant',
    'elephant', 'umbrella', 'together', 'remember'
]
os.makedirs('media/listen/audio', exist_ok=True)
for word in listen_words:
    tts = gTTS(word, lang='en')
    tts.save(f'media/listen/audio/{word}.mp3')
    print(f'✅ listen: {word}.mp3')

# ── Sound Match phonemes ─────────────────────────
phonemes = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    'bl', 'cr', 'st', 'tr', 'sh', 'ch', 'th', 'wh', 'ai', 'ou', 'ee'
]
os.makedirs('media/phonemes/audio', exist_ok=True)
for p in phonemes:
    tts = gTTS(p, lang='en')
    tts.save(f'media/phonemes/audio/{p}.mp3')
    print(f'✅ phoneme: {p}.mp3')

print('\n🎉 All audio generated!')
