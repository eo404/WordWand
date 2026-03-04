from django.urls import path
from . import views

urlpatterns = [
    # Menu (games index)
    path('games/',                views.menu,
         name='menu'),
    # Game pages
    path('games/sound-match/',    views.sound_match,       name='sound_match'),
    path('games/word-builder/',   views.word_builder,      name='word_builder'),
    path('games/sight-word/',     views.sight_word,        name='sight_word'),
    path('games/confusion/',      views.confusion_game,    name='confusion_game'),
    path('games/syllable/',       views.syllable_game,     name='syllable_game'),
    path('games/listen-type/',    views.listen_type,       name='listen_type'),
    path('games/story/',          views.story_builder,     name='story_builder'),


    # AJAX submit endpoints
    path('games/sound-match/submit/',
         views.sound_match_submit,   name='sound_match_submit'),
    path('games/word-builder/submit/',
         views.word_builder_submit,  name='word_builder_submit'),
    path('games/sight-word/submit/',
         views.sight_word_submit,    name='sight_word_submit'),
    path('games/confusion/submit/',
         views.confusion_submit,      name='confusion_submit'),
    path('games/syllable/submit/',
         views.syllable_submit,       name='syllable_submit'),
    path('games/listen-type/submit/',
         views.listen_type_submit,   name='listen_type_submit'),
    path('games/story/submit/',
         views.story_submit,          name='story_submit'),
]
