from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage
from django.core.mail import send_mail
from django.conf import settings

from taggit.models import Tag
from .models import Post
from .forms import EmailPostForm

# Create your views here.
def post_list(request, tag_slug=None):
   
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    # Pagination with 3 posts per page.
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        # If page_number is out of range deliver last page of results.
        posts = paginator.page(paginator.num_pages)
    template_name = 'blog/post/post-list.html'
    context = {'posts': posts, 'tag':tag}
    return render(request, template_name, context)

def post_detail(request, year, month, day, post):
    """Retrives a PUBLISHED post with given slug and publication date."""
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    template_name = 'blog/post/blog-post.html'
    context = {'post': post}

    return render(request, template_name, context)

def post_share(request, post_id):
# Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
        # Form fields passed validation
            cd = form.cleaned_data
            # ... send email
            post_url = request.build_absolute_uri(post.get_absolute_url()) # Build the complete url from post.get_absolute_url
            subject = f"{cd['name']} recommends you read " \
                f"{post.post_title}"
            message = f"Read {post.post_title} at {post_url}\n\n" \
                f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,[cd['to']])
            sent = True
            # return redirect('blog:post_list')
    else:
        form = EmailPostForm()
    template_name = 'blog/post/share.html'
    context = {'post': post,'form': form, 'sent': sent}

    return render(request, template_name, context)