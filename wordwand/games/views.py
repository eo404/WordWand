import json
import random

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import (
    ConfusionAttempt, ConfusionSet,
    ListenAttempt, ListenWord,
    Phoneme, PhonemeAttempt, PhonemeOption,
    SightWord, SightWordAttempt, UserSightWordProgress,
    Story, StoryAttempt,
    SyllableAttempt, SyllableWord,
    UserErrorPattern, UserProgress,
    Word, WordBuildAttempt, WordLetter,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_or_create_progress(user, game_type):
    prog, _ = UserProgress.objects.get_or_create(
        user=user, game_type=game_type)
    return prog


def _calc_stats(records, time_attr='response_time'):
    """
    THE ROOT BUG: every submit view was doing:
        recent = Model.objects.filter(...).order_by(...)[:10]   # sliced QS
        acc = recent.filter(is_correct=True).count() / ...      # CRASHES
        avg_t = sum(a.x for a in recent) / len(recent)          # len() also fails on sliced QS

    Django sliced QuerySets cannot be re-filtered or passed to len().
    Fix: always call list() on the slice first, then work with plain Python.
    This function accepts an already-evaluated list[].
    """
    if not records:
        return 0.0, 0.0
    correct = sum(1 for r in records if r.is_correct)
    acc = round(correct / len(records) * 100, 1)
    avg_t = round(sum(getattr(r, time_attr)
                  for r in records) / len(records), 2)
    return acc, avg_t


def _parse(request):
    return json.loads(request.body)


def _bad(msg, code=400):
    return JsonResponse({'error': msg}, status=code)


# ─── Menu ─────────────────────────────────────────────────────────────────────

@login_required
def menu(request):
    keys = ['sound_match', 'word_builder', 'sight_word',
            'confusion', 'syllable', 'listen_type', 'story_builder']
    prog = {k: _get_or_create_progress(request.user, k) for k in keys}
    return render(request, 'games/menu.html', {
        'sound_progress':     prog['sound_match'],
        'word_progress':      prog['word_builder'],
        'sight_progress':     prog['sight_word'],
        'confusion_progress': prog['confusion'],
        'syllable_progress':  prog['syllable'],
        'listen_progress':    prog['listen_type'],
        'story_progress':     prog['story_builder'],
        'recommended_game':   UserErrorPattern.recommend_game(request.user),
    })


# ─── GAME 1: Sound–Letter Match ───────────────────────────────────────────────

@login_required
def sound_match(request):
    prog = _get_or_create_progress(request.user, 'sound_match')
    phonemes = Phoneme.objects.filter(difficulty_level=prog.level)
    if not phonemes.exists():
        phonemes = Phoneme.objects.all()
    if not phonemes.exists():
        return render(request, 'games/sound_match.html', {'no_data': True, 'progress': prog})

    phoneme = random.choice(list(phonemes))
    options = list(phoneme.options.all())
    if not options:
        return render(request, 'games/sound_match.html', {'no_data': True, 'progress': prog})
    random.shuffle(options)
    return render(request, 'games/sound_match.html',
                  {'phoneme': phoneme, 'options': options, 'progress': prog})


@login_required
@require_POST
def sound_match_submit(request):
    try:
        data = _parse(request)
    except Exception:
        return _bad('Invalid JSON')

    phoneme = get_object_or_404(Phoneme,       pk=data['phoneme_id'])
    option = get_object_or_404(PhonemeOption, pk=data['option_id'])
    resp_time = float(data.get('response_time', 0))

    is_correct = option.is_correct
    PhonemeAttempt.objects.create(
        user=request.user, phoneme=phoneme,
        selected_option=option, is_correct=is_correct,
        response_time=resp_time,
    )
    if not is_correct:
        UserErrorPattern.log(request.user, 'phoneme_miss')

    # FIX: list() the slice so we can iterate and check is_correct
    recent = list(PhonemeAttempt.objects.filter(
        user=request.user).order_by('-attempted_at')[:10])
    acc, avg_t = _calc_stats(recent)
    _get_or_create_progress(
        request.user, 'sound_match').update_after_session(acc, avg_t)

    return JsonResponse({'correct': is_correct, 'accuracy': acc})


# ─── GAME 2: Word Builder ─────────────────────────────────────────────────────

@login_required
def word_builder(request):
    prog = _get_or_create_progress(request.user, 'word_builder')
    words = Word.objects.filter(difficulty_level=prog.level)
    if not words.exists():
        words = Word.objects.all()
    if not words.exists():
        return render(request, 'games/word_builder.html', {'no_data': True, 'progress': prog})

    word = random.choice(list(words))
    # FIX: order_by position so the answer is always deterministic
    letters = list(word.letters.order_by(
        'position').values_list('letter', flat=True))
    shuffled = letters[:]
    random.shuffle(shuffled)
    return render(request, 'games/word_builder.html',
                  {'word': word, 'shuffled': shuffled, 'progress': prog})


@login_required
@require_POST
def word_builder_submit(request):
    try:
        data = _parse(request)
    except Exception:
        return _bad('Invalid JSON')

    word = get_object_or_404(Word, pk=data['word_id'])
    submitted = data['submitted_order']
    resp_time = float(data.get('response_time', 0))

    # FIX: ordered + case-insensitive
    correct_order = list(word.letters.order_by(
        'position').values_list('letter', flat=True))
    is_correct = [s.lower() for s in submitted] == [c.lower()
                                                    for c in correct_order]

    WordBuildAttempt.objects.create(
        user=request.user, word=word,
        submitted_order=submitted, is_correct=is_correct,
        response_time=resp_time,
    )
    if not is_correct:
        UserErrorPattern.log(request.user, 'blending_failure')

    # FIX: list() the slice
    recent = list(WordBuildAttempt.objects.filter(
        user=request.user).order_by('-attempted_at')[:10])
    acc, avg_t = _calc_stats(recent)
    _get_or_create_progress(
        request.user, 'word_builder').update_after_session(acc, avg_t)

    return JsonResponse({'correct': is_correct, 'correct_order': list(correct_order), 'accuracy': acc})


# ─── GAME 3: Sight Word Speed Tap ────────────────────────────────────────────

@login_required
def sight_word(request):
    prog = _get_or_create_progress(request.user, 'sight_word')
    words = SightWord.objects.filter(level=prog.level)
    if not words.exists():
        words = SightWord.objects.all()
    if not words.exists():
        return render(request, 'games/sight_word.html', {'no_data': True, 'progress': prog})

    target = random.choice(list(words))
    distractors = list(SightWord.objects.exclude(
        pk=target.pk).order_by('?')[:3])
    options = distractors + [target]
    random.shuffle(options)
    return render(request, 'games/sight_word.html',
                  {'target': target, 'options': options, 'progress': prog})


@login_required
@require_POST
def sight_word_submit(request):
    try:
        data = _parse(request)
    except Exception:
        return _bad('Invalid JSON')

    target = get_object_or_404(SightWord, pk=data['word_id'])
    selected_id = int(data['selected_id'])
    is_correct = (target.pk == selected_id)
    resp_time = float(data.get('response_time', 0))

    SightWordAttempt.objects.create(
        user=request.user, word=target,
        is_correct=is_correct, response_time=resp_time,
    )
    pw, _ = UserSightWordProgress.objects.get_or_create(
        user=request.user, word=target)
    pw.attempts += 1
    if is_correct:
        pw.correct += 1
    else:
        UserErrorPattern.log(request.user, 'sight_word_miss')
    pw.save()

    # FIX: list() the slice
    recent = list(SightWordAttempt.objects.filter(
        user=request.user).order_by('-attempted_at')[:10])
    acc, avg_t = _calc_stats(recent)
    _get_or_create_progress(
        request.user, 'sight_word').update_after_session(acc, avg_t)

    return JsonResponse({'correct': is_correct, 'accuracy': acc})


# ─── GAME 4: Confusing Letter Fix ────────────────────────────────────────────

@login_required
def confusion_game(request):
    prog = _get_or_create_progress(request.user, 'confusion')
    sets = ConfusionSet.objects.all()
    if not sets.exists():
        return render(request, 'games/confusion.html', {'no_data': True, 'progress': prog})

    confusion = random.choice(list(sets))
    shown = random.choice([confusion.letter_a, confusion.letter_b])
    options = [confusion.letter_a, confusion.letter_b]
    random.shuffle(options)
    return render(request, 'games/confusion.html',
                  {'confusion': confusion, 'shown': shown, 'options': options, 'progress': prog})


@login_required
@require_POST
def confusion_submit(request):
    try:
        data = _parse(request)
    except Exception:
        return _bad('Invalid JSON')

    confusion = get_object_or_404(ConfusionSet, pk=data['confusion_id'])
    shown = data['shown']
    selected = data['selected']
    resp_time = float(data.get('response_time', 0))
    is_correct = (shown == selected)

    ConfusionAttempt.objects.create(
        user=request.user, confusion_set=confusion,
        shown_letter=shown, selected=selected,
        is_correct=is_correct, response_time=resp_time,
    )
    if not is_correct:
        pair = {shown, selected}
        etype = 'bd_confusion' if pair <= {'b', 'd'} else 'pq_confusion'
        UserErrorPattern.log(request.user, etype)

    # FIX: list() the slice
    recent = list(ConfusionAttempt.objects.filter(
        user=request.user).order_by('-attempted_at')[:10])
    acc, avg_t = _calc_stats(recent)
    _get_or_create_progress(
        request.user, 'confusion').update_after_session(acc, avg_t)

    return JsonResponse({'correct': is_correct, 'accuracy': acc})


# ─── GAME 5: Syllable Breaker ─────────────────────────────────────────────────

@login_required
def syllable_game(request):
    prog = _get_or_create_progress(request.user, 'syllable')
    words = SyllableWord.objects.filter(difficulty_level=prog.level)
    if not words.exists():
        words = SyllableWord.objects.all()
    if not words.exists():
        return render(request, 'games/syllable.html', {'no_data': True, 'progress': prog})

    word = random.choice(list(words))
    return render(request, 'games/syllable.html', {'syllable_word': word, 'progress': prog})


@login_required
@require_POST
def syllable_submit(request):
    try:
        data = _parse(request)
    except Exception:
        return _bad('Invalid JSON')

    sw = get_object_or_404(SyllableWord, pk=data['word_id'])
    submitted = data['submitted_splits']
    resp_time = float(data.get('response_time', 0))

    correct = sw.syllable_structure
    # FIX: case-insensitive + strip whitespace
    is_correct = ([s.lower().strip() for s in submitted] ==
                  [c.lower().strip() for c in correct])

    SyllableAttempt.objects.create(
        user=request.user, syllable_word=sw,
        submitted_splits=submitted, is_correct=is_correct,
        response_time=resp_time,
    )
    if not is_correct:
        UserErrorPattern.log(request.user, 'syllable_segmentation')

    # FIX: list() the slice
    recent = list(SyllableAttempt.objects.filter(
        user=request.user).order_by('-attempted_at')[:10])
    acc, avg_t = _calc_stats(recent)
    _get_or_create_progress(
        request.user, 'syllable').update_after_session(acc, avg_t)

    return JsonResponse({'correct': is_correct, 'correct_answer': correct, 'accuracy': acc})


# ─── GAME 6: Listening & Type ─────────────────────────────────────────────────

@login_required
def listen_type(request):
    prog = _get_or_create_progress(request.user, 'listen_type')
    words = ListenWord.objects.filter(difficulty_level=prog.level)
    if not words.exists():
        words = ListenWord.objects.all()
    if not words.exists():
        return render(request, 'games/listen_type.html', {'no_data': True, 'progress': prog})

    word = random.choice(list(words))
    return render(request, 'games/listen_type.html', {'listen_word': word, 'progress': prog})


@login_required
@require_POST
def listen_type_submit(request):
    try:
        data = _parse(request)
    except Exception:
        return _bad('Invalid JSON')

    lw = get_object_or_404(ListenWord, pk=data['word_id'])
    typed = data['typed_answer'].strip().lower()
    resp_time = float(data.get('response_time', 0))
    correct = lw.word_text.strip().lower()
    is_correct = (typed == correct)

    wrong_pos = [i for i in range(
        min(len(typed), len(correct))) if typed[i] != correct[i]]
    if len(typed) != len(correct):
        wrong_pos += list(range(min(len(typed), len(correct)),
                          max(len(typed), len(correct))))

    ListenAttempt.objects.create(
        user=request.user, listen_word=lw,
        typed_answer=typed, is_correct=is_correct,
        wrong_positions=wrong_pos, response_time=resp_time,
    )
    if not is_correct:
        UserErrorPattern.log(request.user, 'phoneme_miss')

    # FIX: list() the slice
    recent = list(ListenAttempt.objects.filter(
        user=request.user).order_by('-attempted_at')[:10])
    acc, avg_t = _calc_stats(recent)
    _get_or_create_progress(
        request.user, 'listen_type').update_after_session(acc, avg_t)

    return JsonResponse({'correct': is_correct, 'wrong_positions': wrong_pos,
                         'correct_word': correct, 'accuracy': acc})


# ─── GAME 7: Story Builder ────────────────────────────────────────────────────

@login_required
def story_builder(request):
    prog = _get_or_create_progress(request.user, 'story_builder')
    stories = Story.objects.filter(difficulty_level=prog.level)
    if not stories.exists():
        stories = Story.objects.all()
    if not stories.exists():
        return render(request, 'games/story_builder.html', {'no_data': True, 'progress': prog})

    story = random.choice(list(stories))
    hard_words = story.get_hard_words()
    return render(request, 'games/story_builder.html', {
        'story':           story,
        'hard_words':      hard_words,
        # FIX: safe JSON for JS data attribute
        'hard_words_json': json.dumps(hard_words),
        'progress':        prog,
    })


@login_required
@require_POST
def story_submit(request):
    try:
        data = _parse(request)
    except Exception:
        return _bad('Invalid JSON')

    story = get_object_or_404(Story, pk=data['story_id'])
    answers = data.get('fill_answers', {})
    time_spent = float(data.get('time_spent', 0))
    if not isinstance(answers, dict):
        answers = {}

    StoryAttempt.objects.create(
        user=request.user, story=story,
        completed=True, fill_answers=answers, time_spent=time_spent,
    )

    # FIX: list() the slice; story uses time_spent not response_time
    recent = list(StoryAttempt.objects.filter(
        user=request.user).order_by('-attempted_at')[:5])
    acc = 80.0
    avg_t = round(sum(a.time_spent for a in recent) /
                  len(recent), 2) if recent else 0
    _get_or_create_progress(
        request.user, 'story_builder').update_after_session(acc, avg_t)

    return JsonResponse({'ok': True, 'accuracy': acc})


# ─── Progress Dashboard ───────────────────────────────────────────────────────

@login_required
def progress_dashboard(request):
    return render(request, 'games/progress.html', {
        'all_progress':     UserProgress.objects.filter(user=request.user).order_by('game_type'),
        'error_patterns':   UserErrorPattern.objects.filter(user=request.user).order_by('-frequency'),
        'recommended_game': UserErrorPattern.recommend_game(request.user),
    })
