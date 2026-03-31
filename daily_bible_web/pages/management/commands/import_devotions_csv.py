import csv
import json
import re
from pathlib import Path
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from pages.models import DailyPage, ReadingLink


DEFAULT_IMAGE = "/static/images/top_banner.jpg"

CATEGORY_IMAGE_MAP = {
    "全心爱主": "/static/images/picture1.jpg",
    "连结社群": "/static/images/picture2.jpg",
    "进入命定": "/static/images/picture3.jpg",
    "成为祝福": "/static/images/picture4.jpg",
}


def normalize_paragraphs(text: str) -> str:
    """
    目标：
    1. 段内换行合并成一段
    2. 段与段之间保留空行（双换行）
    3. 兼容 CSV 中的字面量 \\n
    """
    text = (text or "").strip()
    if not text:
        return text

    # 统一换行
    text = text.replace("\r\n", "")

    lines = [line.strip() for line in text.split("\n")]

    paragraphs = []
    current = []

    for line in lines:
        if not line:
            if current:
                paragraphs.append("".join(current).strip())
                current = []
            continue

        current.append(line)

    if current:
        paragraphs.append("".join(current).strip())

    return "\n".join(p for p in paragraphs if p)


def clean_prayer_text(prayer: str) -> str:
    prayer = normalize_paragraphs(prayer)
    if not prayer:
        return prayer

    match = re.search(r"阿们。", prayer)
    if match:
        return prayer[: match.end()].strip()

    return prayer


class Command(BaseCommand):
    help = "Import devotions from CSV into DailyPage and ReadingLink"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to the CSV file")
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite existing DailyPage rows with the same page_date",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"])
        overwrite = options["overwrite"]

        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        created_pages = 0
        skipped_pages = 0
        overwritten_pages = 0
        created_links = 0

        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            required_columns = {
                "page_date",
                "category",
                "title",
                "readings_text",
                "body",
                "prayer",
                "image_path",
                "reading_links_json",
            }

            missing = required_columns - set(reader.fieldnames or [])
            if missing:
                raise CommandError(
                    f"CSV is missing required columns: {', '.join(sorted(missing))}"
                )

            for row_num, row in enumerate(reader, start=2):
                page_date_raw = (row.get("page_date") or "").strip()
                category = (row.get("category") or "").strip()
                title = (row.get("title") or "").strip()
                body = normalize_paragraphs(row.get("body") or "")
                prayer = clean_prayer_text(row.get("prayer") or "")
                csv_image_path = (row.get("image_path") or "").strip()
                reading_links_json = (row.get("reading_links_json") or "").strip()

                image_path = CATEGORY_IMAGE_MAP.get(category) or csv_image_path or DEFAULT_IMAGE

                if not page_date_raw:
                    raise CommandError(f"Row {row_num}: page_date is empty")
                if not title:
                    raise CommandError(f"Row {row_num}: title is empty")

                try:
                    page_date = datetime.strptime(page_date_raw, "%Y-%m-%d").date()
                except ValueError as e:
                    raise CommandError(
                        f"Row {row_num}: invalid page_date '{page_date_raw}'. Expected YYYY-MM-DD"
                    ) from e

                existing_page = DailyPage.objects.filter(page_date=page_date).first()
                if existing_page:
                    if not overwrite:
                        skipped_pages += 1
                        continue
                    existing_page.delete()
                    overwritten_pages += 1

                daily_page = DailyPage.objects.create(
                    page_date=page_date,
                    title=title,
                    body=body,
                    prayer=prayer,
                    image_path=image_path,
                    category=category,
                )
                created_pages += 1

                links_to_create = []

                if reading_links_json:
                    try:
                        links = json.loads(reading_links_json)
                    except json.JSONDecodeError as e:
                        raise CommandError(
                            f"Row {row_num}: invalid reading_links_json"
                        ) from e

                    if not isinstance(links, list):
                        raise CommandError(
                            f"Row {row_num}: reading_links_json must be a JSON list"
                        )

                    for idx, item in enumerate(links, start=1):
                        if not isinstance(item, dict):
                            raise CommandError(
                                f"Row {row_num}: each reading link must be an object"
                            )

                        ref_text = (item.get("text") or "").strip()
                        url = (item.get("url") or "").strip()

                        if not ref_text:
                            raise CommandError(
                                f"Row {row_num}: reading link #{idx} has empty text"
                            )
                        if not url:
                            raise CommandError(
                                f"Row {row_num}: reading link #{idx} has empty url"
                            )

                        links_to_create.append(
                            ReadingLink(
                                page=daily_page,
                                ref_text=ref_text,
                                url=url,
                                display_order=idx,
                            )
                        )

                if links_to_create:
                    ReadingLink.objects.bulk_create(links_to_create)
                    created_links += len(links_to_create)

        self.stdout.write(
            self.style.SUCCESS(
                "✅ Done | "
                f"Created pages: {created_pages} | "
                f"Skipped pages: {skipped_pages} | "
                f"Overwritten pages: {overwritten_pages} | "
                f"Created links: {created_links}"
            )
        )