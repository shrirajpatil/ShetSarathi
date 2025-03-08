from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CommunityPost
from django.http import HttpResponse

@login_required
def community_home(request):
    if request.user.user_role != 'farmer':
        return HttpResponse("Only farmers can access the community page.", status=403)
    posts = CommunityPost.objects.all().order_by('-created_at')
    return render(request, 'community/community_home.html', {'posts': posts})

@login_required
def add_post(request):
    if request.user.user_role != 'farmer':
        return HttpResponse("Only farmers can post in the community.", status=403)
    if request.method == 'POST':
        content = request.POST.get('content', '')
        if content:
            CommunityPost.objects.create(author=request.user, content=content)
            return redirect('community_home')
        return HttpResponse("Content cannot be empty", status=400)
    return render(request, 'community/add_post.html')