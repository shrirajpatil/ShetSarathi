from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        message = request.POST.get('message', '')
        if not message:
            return JsonResponse({'response': 'No message provided'}, status=200)

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={settings.GOOGLE_API_KEY}"
            headers = {'Content-Type': 'application/json'}
            data = {
                'contents': [{'parts': [{'text': message}]}]
            }
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            reply = response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            print("Gemini Response:", reply)
            return JsonResponse({'response': reply}, status=200)
        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({'response': f"Error: {str(e)}"}, status=200)
    return JsonResponse({'response': 'Invalid request method'}, status=200)