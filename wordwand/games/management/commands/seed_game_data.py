"""
Management command: python manage.py seed_game_data

Creates all the starter content needed for every WordWand game to work:
  - Phonemes + PhonemeOptions  (Sound Match)
  - Words + WordLetters        (Word Builder)
  - SightWords                 (Sight Word Tap)
  - ConfusionSets              (Letter Fix)
  - SyllableWords              (Syllable Breaker)
  - ListenWords                (Listen & Type)  — audio via TTS placeholder
  - Stories                    (Story Builder)

Place this file at:
  your_app/management/commands/seed_game_data.py

Then run:
  python manage.py seed_game_data
"""

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Seeds all WordWand games with starter content'

    def handle(self, *args, **options):
        with transaction.atomic():
            self._seed_phonemes()
            self._seed_words()
            self._seed_sight_words()
            self._seed_confusion_sets()
            self._seed_syllable_words()
            self._seed_listen_words()
            self._seed_stories()
        self.stdout.write(self.style.SUCCESS(
            '✅  All game data seeded successfully!'))

    # ─── GAME 1: Sound Match ──────────────────────────────────────────────────

    def _seed_phonemes(self):
        from games.models import Phoneme, PhonemeOption  # adjust app name if needed

        PHONEMES = [
            # (phoneme_text, difficulty_level, correct_letter, wrong_options)
            ('a',  1, 'a', ['b', 'c', 'd']),
            ('b',  1, 'b', ['d', 'p', 'q']),
            ('c',  1, 'c', ['k', 's', 'g']),
            ('d',  1, 'd', ['b', 'p', 'q']),
            ('e',  1, 'e', ['a', 'i', 'o']),
            ('f',  1, 'f', ['v', 'p', 'b']),
            ('g',  1, 'g', ['j', 'c', 'k']),
            ('h',  1, 'h', ['n', 'm', 'b']),
            ('i',  1, 'i', ['e', 'a', 'o']),
            ('j',  1, 'j', ['g', 'y', 'z']),
            ('k',  1, 'k', ['c', 'g', 'q']),
            ('l',  1, 'l', ['r', 'n', 'i']),
            ('m',  1, 'm', ['n', 'w', 'h']),
            ('n',  1, 'n', ['m', 'u', 'h']),
            ('o',  1, 'o', ['a', 'u', 'e']),
            ('p',  1, 'p', ['b', 'd', 'q']),
            ('r',  1, 'r', ['l', 'w', 'n']),
            ('s',  1, 's', ['c', 'z', 'x']),
            ('t',  1, 't', ['d', 'f', 'l']),
            ('u',  1, 'u', ['o', 'a', 'n']),
            ('v',  1, 'v', ['f', 'b', 'w']),
            ('w',  1, 'w', ['v', 'm', 'u']),
            ('x',  1, 'x', ['z', 's', 'k']),
            ('y',  1, 'y', ['j', 'g', 'i']),
            ('z',  1, 'z', ['s', 'x', 'c']),
            # Level 2 — blends
            ('bl', 2, 'bl', ['cl', 'fl', 'pl']),
            ('cr', 2, 'cr', ['br', 'dr', 'fr']),
            ('st', 2, 'st', ['sk', 'sp', 'sn']),
            ('tr', 2, 'tr', ['dr', 'br', 'gr']),
            # Level 3 — digraphs
            ('sh', 3, 'sh', ['ch', 'th', 'wh']),
            ('ch', 3, 'ch', ['sh', 'th', 'wh']),
            ('th', 3, 'th', ['sh', 'ch', 'wh']),
            ('wh', 3, 'wh', ['sh', 'ch', 'th']),
            # Level 4 — vowel teams
            ('ai', 4, 'ai', ['ay', 'ei', 'ie']),
            ('ou', 4, 'ou', ['ow', 'oi', 'oo']),
            ('ee', 4, 'ee', ['ea', 'ie', 'ei']),
        ]

        created = 0
        for phoneme_text, level, correct, wrongs in PHONEMES:
            ph, made = Phoneme.objects.get_or_create(
                phoneme_text=phoneme_text,
                defaults={'difficulty_level': level,
                          'sound_file': f'phonemes/audio/{phoneme_text}.mp3'}
            )
            if made or not ph.options.exists():
                ph.options.all().delete()
                PhonemeOption.objects.create(
                    phoneme=ph, letter_option=correct, is_correct=True)
                for w in wrongs:
                    PhonemeOption.objects.create(
                        phoneme=ph, letter_option=w, is_correct=False)
                created += 1

        self.stdout.write(f'  Phonemes: {created} created/updated')

    # ─── GAME 2: Word Builder ─────────────────────────────────────────────────

    def _seed_words(self):
        from games.models import Word, WordLetter

        WORDS = [
            # (word_text, difficulty, letters_in_order)
            ('cat',    1, ['c', 'a', 't']),
            ('dog',    1, ['d', 'o', 'g']),
            ('sun',    1, ['s', 'u', 'n']),
            ('hat',    1, ['h', 'a', 't']),
            ('big',    1, ['b', 'i', 'g']),
            ('map',    1, ['m', 'a', 'p']),
            ('run',    1, ['r', 'u', 'n']),
            ('top',    1, ['t', 'o', 'p']),
            ('jump',   2, ['j', 'u', 'm', 'p']),
            ('frog',   2, ['f', 'r', 'o', 'g']),
            ('slip',   2, ['s', 'l', 'i', 'p']),
            ('clap',   2, ['c', 'l', 'a', 'p']),
            ('plant',  2, ['p', 'l', 'a', 'n', 't']),
            ('brush',  3, ['b', 'r', 'u', 'sh']),
            ('chest',  3, ['ch', 'e', 's', 't']),
            ('think',  3, ['th', 'i', 'n', 'k']),
            ('shrimp', 3, ['sh', 'r', 'i', 'm', 'p']),
            ('splash', 4, ['s', 'p', 'l', 'a', 'sh']),
            ('strong', 4, ['s', 't', 'r', 'o', 'n', 'g']),
            ('flight', 4, ['f', 'l', 'i', 'gh', 't']),
        ]

        created = 0
        for word_text, level, letters in WORDS:
            word, made = Word.objects.get_or_create(
                word_text=word_text,
                defaults={'difficulty_level': level}
            )
            if made or not word.letters.exists():
                word.letters.all().delete()
                for pos, letter in enumerate(letters):
                    WordLetter.objects.create(
                        word=word, letter=letter, position=pos)
                created += 1

        self.stdout.write(f'  Words: {created} created/updated')

    # ─── GAME 3: Sight Words ──────────────────────────────────────────────────

    def _seed_sight_words(self):
        from games.models import SightWord

        SIGHT_WORDS = [
            # (word, level)
            ('the',   1), ('and',  1), ('a',    1), ('to',   1), ('is',   1),
            ('in',    1), ('it',   1), ('of',   1), ('you',  1), ('he',   1),
            ('was',   1), ('for',  1), ('on',   1), ('are',  1), ('as',   1),
            ('with',  2), ('his',  2), ('they', 2), ('at',   2), ('be',   2),
            ('this',  2), ('have', 2), ('from', 2), ('or',   2), ('one',  2),
            ('had',   2), ('by',   2), ('word', 2), ('but',  2), ('not',  2),
            ('what',  3), ('all',  3), ('were', 3), ('when', 3), ('your', 3),
            ('said',  3), ('each', 3), ('she',  3), ('do',   3), ('how',  3),
            ('their', 4), ('if',   4), ('will', 4), ('up',   4), ('other', 4),
            ('about', 4), ('out',  4), ('many', 4), ('then', 4), ('them', 4),
        ]

        created = 0
        for word, level in SIGHT_WORDS:
            _, made = SightWord.objects.get_or_create(
                word=word, defaults={'level': level})
            if made:
                created += 1

        self.stdout.write(f'  Sight words: {created} created')

    # ─── GAME 4: Confusion Sets ───────────────────────────────────────────────

    def _seed_confusion_sets(self):
        from games.models import ConfusionSet

        PAIRS = [
            ('b', 'd'),
            ('p', 'q'),
            ('b', 'p'),
            ('d', 'q'),
            ('m', 'n'),
            ('u', 'n'),
        ]

        created = 0
        for a, b in PAIRS:
            _, made = ConfusionSet.objects.get_or_create(
                letter_a=a, letter_b=b)
            if made:
                created += 1

        self.stdout.write(f'  Confusion sets: {created} created')

    # ─── GAME 5: Syllable Words ───────────────────────────────────────────────

    def _seed_syllable_words(self):
        from games.models import SyllableWord

        WORDS = [
            # (word, syllable_structure, difficulty)
            ('apple',      ['ap', 'ple'],          1),
            ('happy',      ['hap', 'py'],           1),
            ('tiger',      ['ti', 'ger'],           1),
            ('winter',     ['win', 'ter'],          1),
            ('butter',     ['but', 'ter'],          1),
            ('summer',     ['sum', 'mer'],          1),
            ('rabbit',     ['rab', 'bit'],          1),
            ('muffin',     ['muf', 'fin'],          1),
            ('banana',     ['ba', 'na', 'na'],      2),
            ('elephant',   ['el', 'e', 'phant'],    2),
            ('umbrella',   ['um', 'brel', 'la'],    2),
            ('potato',     ['po', 'ta', 'to'],      2),
            ('tomato',     ['to', 'ma', 'to'],      2),
            ('remember',   ['re', 'mem', 'ber'],    2),
            ('together',   ['to', 'geth', 'er'],    2),
            ('caterpillar', ['cat', 'er', 'pil', 'lar'], 3),
            ('helicopter', ['hel', 'i', 'cop', 'ter'],  3),
            ('watermelon', ['wa', 'ter', 'mel', 'on'],  3),
            ('alligator',  ['al', 'li', 'ga', 'tor'],   3),
        ]

        created = 0
        for word, structure, level in WORDS:
            _, made = SyllableWord.objects.get_or_create(
                word=word,
                defaults={'syllable_structure': structure,
                          'difficulty_level': level}
            )
            if made:
                created += 1

        self.stdout.write(f'  Syllable words: {created} created')

    # ─── GAME 6: Listen & Type ────────────────────────────────────────────────

    def _seed_listen_words(self):
        from games.models import ListenWord

        WORDS = [
            # (word_text, difficulty)  — audio_file path is a placeholder;
            # upload real .mp3 files via Django admin at listen/audio/<word>.mp3
            ('cat',     1), ('dog',    1), ('sun',    1), ('hat',    1),
            ('red',     1), ('big',    1), ('cup',    1), ('pen',    1),
            ('frog',    2), ('clap',   2), ('step',   2), ('slip',   2),
            ('brush',   2), ('chest',  2), ('think',  2), ('plant',  2),
            ('elephant', 3), ('umbrella', 3), ('together', 3), ('remember', 3),
        ]

        created = 0
        for word_text, level in WORDS:
            _, made = ListenWord.objects.get_or_create(
                word_text=word_text,
                defaults={
                    'difficulty_level': level,
                    'audio_file': f'listen/audio/{word_text}.mp3',
                }
            )
            if made:
                created += 1

        self.stdout.write(f'  Listen words: {created} created')
        self.stdout.write(self.style.WARNING(
            '  ⚠️  Upload real audio files to media/listen/audio/<word>.mp3 '
            'or generate them with a TTS tool.'
        ))

    # ─── GAME 7: Stories ──────────────────────────────────────────────────────

    def _seed_stories(self):
        from games.models import Story

        STORIES = [
            {
                'title': 'The Big Red Dog',
                'content': (
                    'Sam has a big red dog. The dog is called Rex. '
                    'Rex likes to run and jump. He can catch a ball. '
                    'Sam and Rex play in the park every day. '
                    'They are best friends.'
                ),
                'difficulty_level': 1,
                'hard_words': 'catch,every,friends',
                'fill_blanks': [],
            },
            {
                'title': 'The Little Cat',
                'content': (
                    'Lily has a little cat. The cat is white and soft. '
                    'It sits on the mat and drinks milk. '
                    'The cat can jump high. Lily loves her cat very much.'
                ),
                'difficulty_level': 1,
                'hard_words': 'white,drinks,loves',
                'fill_blanks': [],
            },
            {
                'title': 'A Day at the Beach',
                'content': (
                    'Tom and his family went to the beach on Saturday. '
                    'The sun was bright and the sand was warm. '
                    'Tom built a sandcastle near the water. '
                    'His sister collected pretty shells. '
                    'They had ice cream before going home.'
                ),
                'difficulty_level': 2,
                'hard_words': 'family,Saturday,sandcastle,collected,pretty',
                'fill_blanks': [],
            },
            {
                'title': 'The Brave Little Turtle',
                'content': (
                    'Once there was a little turtle who wanted to see the world. '
                    'His friends said he was too slow. But the turtle was determined. '
                    'Every morning he practiced swimming faster. '
                    'One day he crossed the whole pond all by himself. '
                    'Everyone cheered for the brave little turtle.'
                ),
                'difficulty_level': 2,
                'hard_words': 'determined,practiced,crossing,cheered,brave',
                'fill_blanks': [],
            },
            {
                'title': 'Fill the Gaps: The Garden',
                'content': (
                    'The garden was full of beautiful ___. '
                    'A yellow ___ landed on a rose. '
                    'The gardener watered the plants every ___. '
                    'Birds came to eat the ___ from the feeder.'
                ),
                'difficulty_level': 3,
                'hard_words': 'beautiful,butterfly,gardener,feeder',
                'fill_blanks': [[0, 'flowers'], [1, 'butterfly'], [2, 'morning'], [3, 'seeds']],
            },
        ]

        created = 0
        for s in STORIES:
            _, made = Story.objects.get_or_create(
                title=s['title'],
                defaults={
                    'content':          s['content'],
                    'difficulty_level': s['difficulty_level'],
                    'hard_words':       s['hard_words'],
                    'fill_blanks':      s['fill_blanks'],
                }
            )
            if made:
                created += 1

        self.stdout.write(f'  Stories: {created} created')
