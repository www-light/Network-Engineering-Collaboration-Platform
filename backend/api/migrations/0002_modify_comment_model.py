# Generated migration to allow multiple comments per user per post

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        # 移除 unique_together 约束，允许同一用户对同一帖子发表多条评论
        migrations.AlterUniqueTogether(
            name='comment',
            unique_together=set(),
        ),
    ]
