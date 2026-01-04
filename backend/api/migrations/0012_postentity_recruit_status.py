# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_alter_teacherstudentcooperation_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='postentity',
            name='recruit_status',
            field=models.SmallIntegerField(
                choices=[(0, '正在招募'), (1, '招募截止')],
                default=0,
                help_text='招募状态: 0-正在招募, 1-招募截止',
                verbose_name='招募状态'
            ),
        ),
    ]

