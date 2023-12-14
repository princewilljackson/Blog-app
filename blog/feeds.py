import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy
from .models import Post


class LatestsPostsFeed(Feed):
    """
    Feed of latest posts
    """
    title = "Latest Posts"
    link = reverse_lazy('blog:post_list')
    description = "Latest posts from the blog"

    def items(self):
        return Post.published.all()[:5]

    def item_title(self, item):
        return item.post_title

    def item_description(self, item):
        return truncatewords_html(markdown.markdown(item.post_content), 30)
    
    def item_pubdate(self, item):
        return item.publish