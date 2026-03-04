import json
import requests as http

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST


@login_required
def chatbot(request):
    return render(request, 'chatbot/chatbot.html')


@login_required
@require_POST
def chatbot_message(request):
    try:
        data = json.loads(request.body)
        user_msg = data.get('message', '').strip()
        history = data.get('history', [])
    except Exception:
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if not user_msg:
        return JsonResponse({'error': 'Empty message'}, status=400)

    system_prompt = """You are Wanda, a friendly and encouraging reading assistant for children
learning to read. You work inside WordWand, an educational app with 7 games:
1. Sound Match - match sounds to letters
2. Word Builder - drag letters to build words
3. Sight Word Tap - memorise and tap sight words
4. Letter Fix - tell apart b/d/p/q
5. Syllable Breaker - split words into syllables
6. Listen & Type - hear a word and spell it
7. Story Builder - read stories and tap words to hear them

Your personality:
- Warm, patient, and encouraging, never critical
- Use simple language suitable for young children (ages 5-10)
- Use emojis occasionally to keep things fun
- Keep answers short and clear (2-4 sentences max)
- Celebrate effort and progress enthusiastically
- If a child is struggling, offer a gentle tip
- Help with reading, spelling, phonics, and using the games
- If asked something unrelated to learning/reading, kindly redirect

Never say you are an AI or mention Groq/Meta/Llama. You are Wanda!"""

    # Build message list — Groq uses OpenAI-compatible format
    messages = [{'role': 'system', 'content': system_prompt}]
    for msg in history[-10:]:
        if msg.get('role') in ('user', 'assistant') and msg.get('content'):
            messages.append({'role': msg['role'], 'content': msg['content']})
    messages.append({'role': 'user', 'content': user_msg})

    try:
        response = http.post(
            'https://api.groq.com/openai/v1/chat/completions',
            json={
                'model':       'llama-3.3-70b-versatile',
                'max_tokens':  300,
                'temperature': 0.8,
                'messages':    messages,
            },
            headers={
                'Authorization': f'Bearer {settings.GROQ_API_KEY}',
            },
            timeout=20
        )

        if response.status_code != 200:
            return JsonResponse(
                {'error': f'API error {response.status_code}: {response.text}'},
                status=502
            )

        reply = response.json()['choices'][0]['message']['content']

    except http.exceptions.Timeout:
        return JsonResponse({'error': 'Request timed out. Please try again.'}, status=502)
    except http.exceptions.ConnectionError:
        return JsonResponse({'error': 'Could not connect. Check your internet connection.'}, status=502)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=502)

    return JsonResponse({'reply': reply})
