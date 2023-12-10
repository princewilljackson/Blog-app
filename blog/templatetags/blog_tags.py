from django import template
from django.db.models import Count
from blog.models import Post

register = template.Library() # A tag for registering template tags and filters.

@register.simple_tag
def total_posts():
    """Returns the total number of posts published in the blog."""
    return Post.published.count()

@register.inclusion_tag('blog/post/latest_posts.html')# Inclusion tag to render the template given as parameter.
def show_latest_posts(count=5):
    """Returns the lastest posts, limiting it to 5."""
    latest_posts = Post.published.order_by('-publish')[:count]
    context = {'latest_posts': latest_posts}
    return context

@register.simple_tag
def get_most_commented_posts(count=4):
    """build a QuerySet using the annotate() function to aggregate the
    total number of comments for each post, stored in total_comments field."""
    return Post.published.annotate(total_comments=Count('comments')
                                   ).order_by('-total_comments')[:count]