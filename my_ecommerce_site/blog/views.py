from django.shortcuts import render, get_object_or_404
from .models import Blog

def blog_list(request):
    blogs = Blog.objects.all()
    return render(request, 'blog.html', {'blogs': blogs})

def blog_details(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    return render(request, 'blog-details.html', {'blog': blog})
