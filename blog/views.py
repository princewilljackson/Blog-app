from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

from taggit.models import Tag
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, SearchForm

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
    except PageNotAnInteger:
        # If page_number is not an integer deliver the first page
        posts = paginator.page(1)
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
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()
    # List of similar posts
    """The values_list() QuerySet
    returns tuples with the values for the given fields. You pass flat=True to it to get single values
    such as [1, 2, 3, ...] instead of one-tuples such as [(1,), (2,), (3,) ...]."""
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id) # get all posts that contain any of these tags, excluding the current post itself.
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]
    template_name = 'blog/post/blog-post.html'
    context = {'post': post, 'comments':comments, 'form':form, 'similar_posts':similar_posts}

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

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post,
                                                          'form': form,
                                                          'comment': comment})

def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        """We send the form using the GET method instead of POST 
        so that the resulting URL includes the query parameter and is easy to share."""
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('post_title', weight='A') + SearchVector('post_content', weight='B')
            search_query = SearchQuery(query)
            results = Post.published.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query),
                ).filter(rank__gte=0.3).order_by('-rank') # Filter the results to display only ones with rank higher than 0.3.
    template_name = 'blog/post/search.html'
    context = {'form': form,'query': query,'results': results}
    return render(request, template_name, context)