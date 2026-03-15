from django.db import models


class DailyPage(models.Model):
    page_date = models.DateField(unique=True, verbose_name='日期')
    title = models.CharField(max_length=255, blank=True, verbose_name='标题')
    body = models.TextField(verbose_name='灵修内容')
    prayer = models.TextField(blank=True, verbose_name='祷告内容')
    image_path = models.CharField(max_length=1000, blank=True, verbose_name='图片路径')

    class Meta:
        ordering = ['page_date']
        verbose_name = '每日页面'
        verbose_name_plural = '每日页面'

    def __str__(self) -> str:
        return self.title or f'{self.page_date} 每日读经'


class ReadingLink(models.Model):
    page = models.ForeignKey(
        DailyPage,
        related_name='reading_links',
        on_delete=models.CASCADE,
        verbose_name='所属页面',
    )
    ref_text = models.CharField(max_length=255, verbose_name='经文显示文字')
    url = models.URLField(max_length=1000, verbose_name='经文链接')
    display_order = models.PositiveIntegerField(default=0, verbose_name='显示顺序')

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = '读经链接'
        verbose_name_plural = '读经链接'

    def __str__(self) -> str:
        return self.ref_text
