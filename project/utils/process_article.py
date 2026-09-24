
from scraper.models import NewsArticle,ChangedNewsArticle,Source, NewsImage
import base64
import requests
from utils.check_keyword import check_keywords_for_article

def image_url_to_base64(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")
    except Exception as e:
        print(f"[⚠️ BASE64 Error] {url} - {e}")
        return None


def process_article_data(link, title, description, content, image_url, gallery_images, news_shared_date, source_link):
    from scraper.models import Source, NewsArticle, ChangedNewsArticle, NewsImage
    from utils.photo_save import download_and_resize_image

    def normalize_text(value):
        return (value or "").replace("\xa0", " ").strip()

    clean_gallery = [g for g in (gallery_images or []) if g and g.strip()]

    if not any([
        normalize_text(title),
        normalize_text(description),
        normalize_text(content),
        image_url and image_url.strip(),
        clean_gallery,
        news_shared_date
    ]):
        return

    try:
        source_instance = Source.objects.get(link=source_link)
    except Source.DoesNotExist:
        return

    existing_article = NewsArticle.objects.filter(url=link).first()

    if existing_article:
        title_changed = existing_article.title != title
        content_changed = existing_article.content != content
        description_changed = existing_article.description != description

        existing_main_image = existing_article.images.filter(is_main=True).first()
        main_image_changed = (existing_main_image.image_url if existing_main_image else None) != image_url

        existing_gallery_urls = set(img.image_url for img in existing_article.images.filter(is_main=False))
        new_gallery_urls = set(gallery_images or [])
        gallery_changed = existing_gallery_urls != new_gallery_urls

        has_meaningful_change = any([title_changed, content_changed, description_changed])
        has_image_change = main_image_changed or (gallery_changed and bool(new_gallery_urls))

        if has_meaningful_change or has_image_change:
            changed_article = ChangedNewsArticle.objects.create(
                newsarticle=existing_article,
                title=existing_article.title if title_changed else None,
                description=existing_article.description if description_changed else None,
                content=existing_article.content if content_changed else None,
            )

            for img in existing_article.images.all():
                NewsImage.objects.create(
                    changed_newsarticle=changed_article,
                    image_url=img.image_url,
                    local_image_url=img.local_image_url,
                    is_main=img.is_main,
                )

            existing_article.title = title
            existing_article.description = description
            existing_article.content = content
            existing_article.news_shared_date = news_shared_date
            existing_article.save()

            check_keywords_for_article(existing_article)
            
            
            existing_article.images.all().delete()

            if image_url:
                file_content = download_and_resize_image(image_url, instance=existing_article)
                NewsImage.objects.create(
                    newsarticle=existing_article,
                    image_url=image_url,
                    local_image_url=file_content,
                    is_main=True
                )

            for g_url in set(gallery_images or []):
                file_content = download_and_resize_image(g_url, instance=existing_article)
                NewsImage.objects.create(
                    newsarticle=existing_article,
                    image_url=g_url,
                    local_image_url=file_content,
                    is_main=False
                )

    else:
        new_article = NewsArticle.objects.create(
            source=source_instance,
            url=link,
            title=title,
            description=description,
            content=content,
            news_shared_date=news_shared_date,
        )
        news_img_url=NewsImage.objects.create(
            newsarticle=new_article,
            image_url=image_url,
            is_main=True
        )

        
        
        #check_keywords_for_article(new_article)

        if image_url:
            file_content = download_and_resize_image(image_url, instance=new_article)
            # NewsImage.objects.create(
            #     newsarticle=new_article,
            #     image_url=image_url,
            #     local_image_url=file_content,
            #     is_main=True
            # )


            NewsImage.objects.filter(newsarticle=new_article, is_main=True).update(local_image_url=file_content)

        for g_url in set(gallery_images or []):
            file_content = download_and_resize_image(g_url, instance=new_article)
            NewsImage.objects.create(
                newsarticle=new_article,
                image_url=g_url,
                local_image_url=file_content,
                is_main=False
            )
            






def process_article_data_telegram(source_name, link, title, content, gallery_images=None, news_shared_date=None):

    def normalize_text(value):
        return (value or "").replace("\xa0", " ").strip()

    gallery_images = gallery_images or []
    clean_gallery = [g for g in gallery_images if g.get("image_url")]

    if not any([
        normalize_text(title),
        normalize_text(content),
        clean_gallery,
        news_shared_date
    ]):
        return

    try:
        source_instance = Source.objects.get(name=source_name)
    except Source.DoesNotExist:
        return None

    existing_article = NewsArticle.objects.filter(url=link).first()

    if existing_article:
        title_changed = existing_article.title != title
        content_changed = existing_article.content != content

        existing_main = existing_article.images.filter(is_main=True).first()
        main_old_url = existing_main.image_url if existing_main else None
        new_main_url = clean_gallery[0]["image_url"] if clean_gallery else None
        main_image_changed = main_old_url != new_main_url

        existing_gallery_urls = set(img.image_url for img in existing_article.images.filter(is_main=False))
        new_gallery_urls = set(g["image_url"] for g in clean_gallery[1:])
        gallery_changed = existing_gallery_urls != new_gallery_urls

        has_meaningful_change = any([title_changed, content_changed])
        has_image_change = main_image_changed or gallery_changed

        if has_meaningful_change or has_image_change:
            changed_article = ChangedNewsArticle.objects.create(
                newsarticle=existing_article,
                title=existing_article.title if title_changed else None,
                content=existing_article.content if content_changed else None,
            )

            for img in existing_article.images.all():
                NewsImage.objects.create(
                    changed_newsarticle=changed_article,
                    image_url=img.image_url,
                    local_image_url=img.local_image_url,
                    is_main=img.is_main,
                )

            existing_article.title = title
            existing_article.content = content
            existing_article.news_shared_date = news_shared_date
            existing_article.save()

            check_keywords_for_article(existing_article)

            existing_article.images.all().delete()

            if clean_gallery:
                first = clean_gallery[0]
                NewsImage.objects.create(
                    newsarticle=existing_article,
                    image_url=first["image_url"],
                    local_image_url=first["django_file"],
                    is_main=True
                )

            for g in clean_gallery[1:]:
                NewsImage.objects.create(
                    newsarticle=existing_article,
                    image_url=g["image_url"],
                    local_image_url=g["django_file"],
                    is_main=False
                )

        return existing_article

    
    

    new_article = NewsArticle.objects.create(
        source=source_instance,
        url=link,
        title=title,
        content=content,
        news_shared_date=news_shared_date,
    )

    check_keywords_for_article(new_article)

    if clean_gallery:
        first = clean_gallery[0]
        NewsImage.objects.create(
            newsarticle=new_article,
            image_url=first["image_url"],
            local_image_url=first["django_file"],
            is_main=True
        )

    for g in clean_gallery[1:]:
        NewsImage.objects.create(
            newsarticle=new_article,
            image_url=g["image_url"],
            local_image_url=g["django_file"],
            is_main=False
        )

    return new_article