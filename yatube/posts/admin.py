from django.contrib import admin

from posts.models import Post, Group, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    list_editable = ('group',)
    list_display = ('pk', 'text', 'pub_date', 'author', 'group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = ('slug',
                    'title',
                    'description')
    search_fields = ('title',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('post',
                    'author',
                    'text',
                    'created')
    search_fields = ('author__username', 'text')
    list_filter = ('created',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'author',
                    'pk')
    search_fields = ('author__username', 'user__username')


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
