from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, "child/home.html")

@login_required
def letters_intro(request):
    return render(request, "learning/letters_intro.html")


@login_required
def alphabetgrid(request):
    return render(request, "learning/alphabetgrid.html")
