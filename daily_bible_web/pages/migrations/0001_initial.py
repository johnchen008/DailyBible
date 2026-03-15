from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='DailyPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page_date', models.DateField(unique=True, verbose_name='日期')),
                ('title', models.CharField(blank=True, max_length=255, verbose_name='标题')),
                ('body', models.TextField(verbose_name='灵修内容')),
                ('prayer', models.TextField(blank=True, verbose_name='祷告内容')),
                ('image_path', models.CharField(blank=True, max_length=1000, verbose_name='图片路径')),
            ],
            options={
                'verbose_name': '每日页面',
                'verbose_name_plural': '每日页面',
                'ordering': ['page_date'],
            },
        ),
        migrations.CreateModel(
            name='ReadingLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ref_text', models.CharField(max_length=255, verbose_name='经文显示文字')),
                ('url', models.URLField(max_length=1000, verbose_name='经文链接')),
                ('display_order', models.PositiveIntegerField(default=0, verbose_name='显示顺序')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reading_links', to='pages.dailypage', verbose_name='所属页面')),
            ],
            options={
                'verbose_name': '读经链接',
                'verbose_name_plural': '读经链接',
                'ordering': ['display_order', 'id'],
            },
        ),
    ]
