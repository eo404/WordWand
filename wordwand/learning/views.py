from django.shortcuts import render


def home(request):
    return render(request, "child/home.html")


def letters_intro(request):
    return render(request, "learning/letters_intro.html")

def alphabetgrid(request):
    return render(request, "learning/alphabetgrid.html")
