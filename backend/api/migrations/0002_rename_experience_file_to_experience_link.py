# Generated migration to rename experience_file to experience_link

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skillinformation',
            name='experience_link',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='经验链接'),
        ),
    ]
