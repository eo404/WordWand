from django.shortcuts import render


def home(request):
    return render(request, "child/home.html")


def letters_intro(request):
    return render(request, "learning/letters_intro.html")

def alphabetgrid(request):
    return render(request, "learning/alphabetgrid.html")


def letter(request, letter):
    return render(request, "learning/letter.html", {
        "letter": letter.upper()
    })


def letter_video(request, letter):
    return render(request, "learning/letter_video.html", {
        "letter": letter.upper()
    })


def letter_trace(request, letter):
    return render(request, "learning/letter_trace.html", {
        "letter": letter.upper()
    })
