from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required


VALID_LETTERS = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')


def _letter_context(letter):
    """Normalise and validate a letter parameter."""
    letter = letter.upper()
    if letter not in VALID_LETTERS:
        from django.http import Http404
        raise Http404(f"Invalid letter: {letter}")
    return {"letter": letter}


def home(request):
    return render(request, "child/home.html")


@login_required
def letters_intro(request):
    return render(request, "learning/letters_intro.html")


@login_required
def alphabetgrid(request):
    return render(request, "learning/alphabetgrid.html")


@login_required
def letter(request, letter):
    return render(request, "learning/letter.html", _letter_context(letter))


@login_required
def letter_video(request, letter):
    return render(request, "learning/letter_video.html", _letter_context(letter))


@login_required
def letter_trace(request, letter):
    return render(request, "learning/letter_trace.html", _letter_context(letter))
