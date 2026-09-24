from bs4 import BeautifulSoup,Tag
import re


def clean_soup_tags(soup: BeautifulSoup, container: Tag) -> None:
    
    for tag in container.find_all(['script', 'iframe', 'video']):
        tag.decompose()

    for a_tag in container.find_all('a'):
        if a_tag and a_tag.has_attr('href'):
            new_a_tag = soup.new_tag('a', href=a_tag['href'])
            new_a_tag.string = a_tag.get_text(strip=True)
            a_tag.replace_with(new_a_tag)
        else:
            a_tag.decompose()
            
            
            
def clean_soup_images(soup: BeautifulSoup, container: Tag) -> None:
    for image in container.find_all('img'):
        if image and image.has_attr('src'):
            new_img_tag = soup.new_tag('img', src=image['src'])
            image.replace_with(new_img_tag)
        else:
            image.decompose()
            
            
def extract_gallery_images(news_content):
   
    gallery_images = []
    images = news_content.find_all('img')

    for image in images: 
        src = None
        if image and image.has_attr('data-src'):
            src = image['data-src'].strip()
        elif image and image.has_attr('src'):
            src = image['src'].strip()

        if src:
            gallery_images.append(src)

    for img in images:
        img.decompose()

    return gallery_images
            
def clean_html_withregex(content: str) -> str:
    if not content:
        return None

    content = re.sub(r'<div>\s*</div>', '', content)

    content = re.sub(r'<div>\s*(<div>\s*</div>\s*)+\s*</div>', '', content)

    content = re.sub(r'<div>\s*<svg[^>]*?>[\s\S]*?</svg>\s*</div>', '', content)

    content = re.sub(r'(<div>\s*){2,}(</div>\s*){2,}', '', content)

    content = re.sub(r'\n\s*\n+', '\n', content)

    content = re.sub(r'<\s*br\s*/?>', ' ', content, flags=re.IGNORECASE)

    content = re.sub(r'<\s*/?\s*o:p\s*>', '', content, flags=re.IGNORECASE)

    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

    content = re.sub(r'^\s*\n', '', content, flags=re.MULTILINE)

    return content


def extract_relevant_content(content_element):
    filtered_content = BeautifulSoup("", 'html.parser')

    for tag in content_element.find_all(['p', 'img', 'iframe', 'div']):
        if tag.name == 'p':
            new_p_content = ""
            
            for child in tag.children:
                if isinstance(child, str):  
                    new_p_content += child.strip()
                elif child.name == 'a' and child.get_text(strip=True):  
                    if new_p_content and not new_p_content.endswith(' '):
                        new_p_content += ' '
                    new_p_content += child.get_text(strip=True) + ' '  
                elif child.get_text(strip=True): 
                    child_text = child.get_text(strip=True)
                    
                    if new_p_content and not new_p_content.endswith(' '): 
                        new_p_content += ' '
                    
                    new_p_content += child_text 

            tag.string = new_p_content.strip()  
            if tag.string == '':  
                tag.extract()
                
        if tag.name == 'div':
            new_div_content = ""
            
            if 'class' in tag.attrs and 'AdviadNativeVideo' in tag['class']:
                continue  
            tag_text = tag.get_text(strip=True)
            
            if not tag_text and ('itemprop' in tag.attrs or 'itemscope' in tag.attrs):
                continue  

            for child in tag.children:
                if isinstance(child, str): 
                    new_div_content += child.strip()
                elif child.name == 'a' and child.get_text(strip=True):  
                    if new_div_content and not new_div_content.endswith(' '):
                        new_div_content += ' '
                    new_div_content += child.get_text(strip=True) + ' '  
                elif child.get_text(strip=True):  
                    child_text = child.get_text(strip=True)
                    
                    if new_div_content and not new_div_content.endswith(' '):
                        new_div_content += ' '

                    new_div_content += child_text 

            tag.string = new_div_content.strip() 
            if tag.string == '':  
                tag.extract()
                
        if tag.name == 'img':
            tag.string = tag.get_text(strip=True)
            if tag.string == '': 
                tag.extract()
            
        filtered_content.append(tag)

    return filtered_content.prettify()



#saytlar ucun clean funksiya


def clean_oxu(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    unwanted_div_classes = ["gallery-area", "gallery-slide swiper", "swiper-wrapper", "swiper-slide", "gallery-thumbs-slide","swiper","swiper-button-next swiper-control",
                            "swiper-button-prev swiper-contro"]
    
    #istenmeyen div classlari silir
    for div_class in unwanted_div_classes:
        for div in soup.find_all("div", class_=div_class):
            div.decompose()
            
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
            
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}  
    
    return str(soup)
 


def clean_apa(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    unwanted_div_classes = ["rek_banner_mobile mt-site mb-site","tags mt-site","logo","links" ]

    #istenmeyen div classlari silir
    for div_class in unwanted_div_classes:
        for div in soup.find_all("div", class_=div_class):
            div.decompose()
            
            
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
    
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}  
    
    unwanted_img_prefixes = ["https://apa.az/storage/authors/", "https://apa.az/site/assets/images/icons/"]
    
    for img in soup.find_all("img", src=True): 
        if any(img["src"].startswith(prefix) for prefix in unwanted_img_prefixes):
            img.decompose()
            
    cleaned_html = str(soup)
    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()
    
    
    
    
def clean_report(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    unwanted_div_classes = ["subs-in-social subs-telegram","icon","subs-message","subs-in-social subs-whatsapp","news-gallery","swiper-wrapper","news-gallery"]
    
    #istenmeyen div classlari silir
    for div_class in unwanted_div_classes:
        for div in soup.find_all("div", class_=div_class):
            div.decompose()
            
            
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
            
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}  
            

    
    
    cleaned_html = str(soup)
    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()



def clean_editor(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    unwanted_div_classes = [
        "subs-in-social subs-telegram","subs-in-social subs-youtube", "subs-in-social subs-instagram","icon", "subs-message", "subs-in-social subs-whatsapp", 
        "subs-in-social subs-facebook", "social-follow", "clearfix", "fb-comments", "fb-background-color", 
        "lSSlideWrapper usingCss", "lSSlideOuter", "article-gallery", "gallery-area"
    ]
    
    unwanted_div_ids = ["MILLI_Slot_Mobile_320x100_under_news_text"]

    for div_class in unwanted_div_classes:
        for div in soup.find_all("div", class_=div_class):
            div.decompose()
            
    for div_id in unwanted_div_ids:
        for div in soup.find_all("div", id=div_id):
            div.decompose()
            
    for div in soup.find_all("div", class_=True): 
        if any(cls.startswith("swiper") for cls in div["class"]): 
            div.decompose()
            
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
            
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}  
    
    cleaned_html = str(soup)
    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()


def clean_xezerxeber(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    unwanted_div_classes = [
        "ad-video-container-67ee354348f17",
    ]
    

    for div_class in unwanted_div_classes:
        for div in soup.find_all("div", class_=div_class):
            div.decompose()
            
            
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
            
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}

    cleaned_html = str(soup)
    cleaned_html = re.sub(r'inPage|Inpage', ' ', cleaned_html)

    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()

def clean_azxeber(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
            
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
    
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}  
    
    unwanted_img_prefixes = ["https://azxeber.com/file/articles/"]
    
    for img in soup.find_all("img", src=True): 
        if any(img["src"].startswith(prefix) for prefix in unwanted_img_prefixes):
            img.decompose()
            
    cleaned_html = str(soup)
    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()



def clean_lent(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
            
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
    
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}  
            
    cleaned_html = str(soup)
    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()



def clean_metbuat(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    unwanted_div_classes = [
        "alert alert-danger", "fb-like",
    ]
    
    unwanted_div_ids = ["fb-root"]

    for div_class in unwanted_div_classes:
        for div in soup.find_all("div", class_=div_class):
            div.decompose()
            
    for div_id in unwanted_div_ids:
        for div in soup.find_all("div", id=div_id):
            div.decompose()
            
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
            
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}

    cleaned_html = str(soup)
    cleaned_html = re.sub(r'inPage|Inpage', ' ', cleaned_html)

    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()



def clean_trend(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
            
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}

    cleaned_html = str(soup)
    cleaned_html = re.sub(r'inPage|Inpage', ' ', cleaned_html)

    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()



def clean_milli(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
            
    for tag in soup.find_all(["div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
            
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}

    cleaned_html = str(soup)
    cleaned_html = re.sub(r'inPage|Inpage', ' ', cleaned_html)

    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()



def clean_armeniatoday(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    unwanted_div_classes = [
        "jeg_post_tags", "telegram-banner",
    ]
    
    for img in soup.find_all("img", alt=True):
        if "telegram" in img["alt"].lower():
            img.decompose()

    for div_class in unwanted_div_classes:
        for div in soup.find_all("div", class_=div_class):
            div.decompose()
            
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
            
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}

    cleaned_html = str(soup)
    cleaned_html = re.sub(r'inPage|Inpage', ' ', cleaned_html)

    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()



def clean_izru(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
            
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
    
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}  
            
    cleaned_html = str(soup)
    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()

def clean_infoxru(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
            
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
    
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}  
            
    cleaned_html = str(soup)
    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()


def clean_mirror(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
            
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
    
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}  
            
    cleaned_html = str(soup)
    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()





def clean_anlatilaninotesi(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
            
    for tag in soup.find_all(["div", "p","a"]):
        tag.attrs = {}

    cleaned_html = str(soup)
    cleaned_html = re.sub(r'inPage|Inpage', ' ', cleaned_html)

    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()


def clean_dwcom(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
            
    for tag in soup.find_all(["div", "p","a"]):
        tag.attrs = {}
        
    for img in soup.find_all("img"):
        data_url = img.get("data-url")
        if data_url and "${formatId}" in data_url:
            new_url = data_url.replace("${formatId}", "906")
            img["src"] = new_url 
            del img["data-url"]  
        


    cleaned_html = str(soup)
    cleaned_html = re.sub(r'inPage|Inpage', ' ', cleaned_html)

    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()


def clean_ulusal(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
            
    for tag in soup.find_all(["div", "p","a"]):
        tag.attrs = {}
        
    cleaned_html = str(soup)
    cleaned_html = re.sub(r'inPage|Inpage', ' ', cleaned_html)

    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()


def clean_voaturkce(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
            
    for tag in soup.find_all(["div", "p","a"]):
        tag.attrs = {}
        
    cleaned_html = str(soup)
    cleaned_html = re.sub(r'inPage|Inpage', ' ', cleaned_html)

    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()


def clean_bianet(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')

    # <a class="ccard ccard--news ccard--news-content"> içindeki her şeyi kaldır
    cleaned_html = re.sub(r'<a class="ccard ccard--news ccard--news-content".*?</a>', '', str(soup), flags=re.DOTALL)
                                        
    # Boş <p> ve <div> etiketlerini temizle
    soup = BeautifulSoup(cleaned_html, 'html.parser')
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()

    # Gereksiz attribute'leri temizle
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}

    # Fazla boşlukları temizle
    cleaned_html = str(soup)
    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()

def clean_birgun(content_element):

    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    unwanted_div_classes  = soup.find_all('div')

    
    # unwanted_div_ids = ["fb-root"]

    for div in unwanted_div_classes:
        div.decompose()
            
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()

    # Fazla boşlukları temizle
    cleaned_html = str(soup)
    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()



def clean_agos(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    unwanted_div_classes = [
        "tagcloud", "cf",
    ]

    for div_class in unwanted_div_classes:
        for div in soup.find_all("div", class_=div_class):
            div.decompose()
            
    for tag in soup.find_all(["div","p"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
            
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div","style","span","button","blockquote","section","b","figure","figcaption","h2","h1","h3","ol","td","table"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
            
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p","style","span","button","blockquote","section","b","figure","figcaption","h2","h1","h3","ol","td","table"]):
        tag.attrs = {}  
    
    return str(soup)

def clean_gercekgundem(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    unwanted_div_classes = [
        "adpro desktop-ad text-center mh-280","mceNonEditable related-news",
    ]
    
    unwanted_p_classes = [
        "news-source"
    ]

    for div_class in unwanted_div_classes:
        for div in soup.find_all("div", class_=div_class):
            div.decompose()
            
    for p_class in unwanted_p_classes:
        for p in soup.find_all("p", class_=p_class):
            p.decompose()
            
    for tag in soup.find_all(["div","p"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
            
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}
        
    for img in soup.find_all("img"):
        if img.get("height") == "99" and img.get("width") == "176":
            img.decompose()

    cleaned_html = str(soup)
    cleaned_html = re.sub(r'inPage|Inpage', ' ', cleaned_html)

    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()



def clean_sabah(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
            
    for tag in soup.find_all(["div","p"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
            
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}

    cleaned_html = str(soup)
    cleaned_html = re.sub(r'inPage|Inpage', ' ', cleaned_html)

    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()

def clean_samanyoluhaber(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
            
    for tag in soup.find_all(["div","p"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
            
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}

    cleaned_html = str(soup)
    cleaned_html = re.sub(r'inPage|Inpage', ' ', cleaned_html)

    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()



def clean_cumhuriyet(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
            
    for tag in soup.find_all(["div","p"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
            
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}

    cleaned_html = str(soup)
    cleaned_html = re.sub(r'inPage|Inpage', ' ', cleaned_html)

    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()


def clean_sozcu(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
            
    for tag in soup.find_all(["div","p"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
            
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}

    cleaned_html = str(soup)
    cleaned_html = re.sub(r'inPage|Inpage', ' ', cleaned_html)

    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()

def clean_haberler(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    unwanted_div_classes = ["orderFlex", "hbptItem", "editorSade", "hbptAuthorName", "hbptAuthorJob","hbnwboxigB","hbptAuthorImg","lnarea hbptDetail",
                            "info-text"]
    unwanted_div_ids = ["nwsKeywords"]
    unwanted_p_classes = []
    unwanted_p_ids = ["inpage_reklam"]

    for div_class in unwanted_div_classes:
        for div in soup.find_all("div", class_=div_class):
            div.decompose()
    
    for div_id in unwanted_div_ids:
        for div in soup.find_all("div", id=div_id):
            div.decompose()
            
    for p_id in unwanted_p_ids:
        for p in soup.find_all("p",id=p_id):
            div.decompose()
            
    for img in soup.find_all("img", alt="Reklam"):
        img.decompose()
        
        
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
    
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
            
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}  
    
    return str(soup)
    
    
    
def clean_rasthaber(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')

    for tag in soup.find_all(["div", "p"]):
        if not tag.text.strip() and not tag.find():
            tag.decompose()

    for tag in soup.find_all(["div", "p", "section","h2"]):
        tag.attrs = {}

    for img in soup.find_all("img"):
        if img.has_attr("src") and img["src"].startswith("data:image"):
            img.decompose()

    for op_tag in soup.find_all("o:p"):
        op_tag.decompose()
        
    cleaned_html = str(soup)
    cleaned_html = re.sub(r'inPage|Inpage', ' ', cleaned_html)
    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()
    
    
    
def clean_yeniakit(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    unwanted_div_classes = [
        "similarNews", "similarItemImage","similarItemText","similarItemCat","similarItemTitle","ads",
    ]
    
    for div_class in unwanted_div_classes:
        for div in soup.find_all("div", class_=div_class):
            div.decompose()
            
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
            
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}

    cleaned_html = str(soup)
    cleaned_html = re.sub(r'inPage|Inpage', ' ', cleaned_html)

    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()
  
    
    
    
def clean_yenisafak(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    unwanted_div_classes = [
        "news-detail-ads",
    ]
    

    for div_class in unwanted_div_classes:
        for div in soup.find_all("div", class_=div_class):
            div.decompose()
            
    
    for tag in soup.find_all(["div", "p", "span", "figure","strong","i", "figcaption", "h2"]):
        if not tag.text.strip() and not tag.find():
            tag.decompose()

    for tag in soup.find_all(["div", "p", "span", "figure","strong","i", "figcaption", "h2"]):
        tag.attrs = {}

    

    cleaned_html = str(soup)

    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()




def clean_milliyet(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    unwanted_div_classes = [
        "section-container-content","interesting","medyanet-inline-adv","medyanet-outstream-mobile adRenderer"
    ]
    
    # unwanted_div_ids = ["postici"]

    for div_class in unwanted_div_classes:
        for div in soup.find_all("div", class_=div_class):
            div.decompose()
            
    # for div_id in unwanted_div_ids:
    #     for div in soup.find_all("div", id=div_id):
    #         div.decompose()
            
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
            
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}

    cleaned_html = str(soup)
    cleaned_html = re.sub(r'inPage|Inpage', ' ', cleaned_html)

    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()



def clean_aa(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    unwanted_div_classes = ["detay-paylas"]
    unwanted_span_classes = ["detay-foto-editor"]

    for div_class in unwanted_div_classes:
        for div in soup.find_all("div", class_=div_class):
            div.decompose()
    
    for span_class in unwanted_span_classes:
        for span in soup.find_all("span", class_=span_class):  
            span.decompose()
    
        
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose() 
    
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}

    cleaned_html = str(soup)
    cleaned_html = re.sub(r'inPage|Inpage', ' ', cleaned_html)
    cleaned_html = re.sub(r'\n\s*\n+', '\n', cleaned_html) 

    return cleaned_html.strip()






def clean_kronos38(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    unwanted_div_classes = ["code-block code-block-1"]
    
    unweanted_div_ids = ["postici"]
    
    #istenmeyen div classlari silir
    for div_class in unwanted_div_classes:
        for div in soup.find_all("div", class_=div_class):
            div.decompose()
            
    for div_id in unweanted_div_ids:
        for div_id in soup.find_all('div',id=div_id):
            div_id.decompose()
    
    
    
    
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
            
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}  
    
    return str(soup)
 



def clean_unian_net(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
            
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}  
    
    return str(soup)
 
 
 
def clean_belta_by(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
            
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p"]):
        tag.attrs = {}  
    
    return str(soup)


def clean_nv_ua(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div", "span","i"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
            
    for div in soup.find_all("div"):
        text = div.get_text(strip=True)
        if text.lower() == "читать далее".lower():  
            div.decompose()

    for tag in soup.find_all(["div", "p", "span","i"]):
        tag.attrs = {}  
    
    return str(soup)


def clean_az_sputniknews_ru(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div","svg","use","style"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
            
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p","svg","use","style"]):
        tag.attrs = {}  
    
    return str(soup)



def clean_az_centralasia_media(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div","svg","use","style","span"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
        
    
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p","svg","use","style","span"]):
        tag.attrs = {}  
    
    return str(soup)


def clean_nur_kz(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div","svg","use","style","span","strong","i","figure",'figcaption',"source","blockquote"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
        
    
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p","svg","use","style","span","strong","i","figure",'figcaption',"source"]):
        tag.attrs = {}  
    
    return str(soup)



def clean_orda_kz(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    for tag in soup.find_all(["p", "div","svg","use","style","span","strong","i","figure",'figcaption',"source","blockquote"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
        
    
    for tag in soup.find_all(["div", "p","svg","use","style","span","strong","i","figure",'figcaption',"source","blockquote"]):
        tag.attrs = {}  
    
    return str(soup)



def clean_uz_sputniknews_ru(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div","svg","use","style","aside","span"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
            
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p","svg","use","style","aside","span"]):
        tag.attrs = {}  
    
    return str(soup)



def clean_norharatch_com(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div","svg","use","style","aside","span","h3"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
            
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p","svg","use","style","aside","span","h3"]):
        tag.attrs = {}  
    
    return str(soup)



def clean_newsgeorgia_ge(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div","style","span","button"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
            
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p","style","span","button"]):
        tag.attrs = {}  
    
    return str(soup)


def clean_formulanews_ge(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div","style","span","button","blockquote","section"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
            
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p","style","span","button","blockquote","section"]):
        tag.attrs = {}  
    
    return str(soup)




def clean_yerevan_today(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div","style","span","button","blockquote","section","ol"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
            
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p","style","span","button","blockquote","section","ol"]):
        tag.attrs = {}  
    
    return str(soup)



def clean_aravot_am(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div","style","span","button","blockquote","section","ol","td"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
            
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p","style","span","button","blockquote","section","ol","td"]):
        tag.attrs = {}  
    
    return str(soup)



def clean_infoport_am(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div","style","span","button","blockquote","section","ol","td","li","ul","i"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
            
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p","style","span","button","blockquote","section","ol","td","li","ul","i"]):
        tag.attrs = {}  
    
    return str(soup)


def clean_armenpress_am(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div","style","span","button","blockquote","section","ap-article"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
            
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p","style","span","button","blockquote","section","ap-article"]):
        tag.attrs = {}  
    
    return str(soup)


def clean_armenianweekly_com(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div","style","span","button","blockquote","section","b","figure","figcaption"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
            
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p","style","span","button","blockquote","section","b","figure","figcaption"]):
        tag.attrs = {}  
    
    return str(soup)



def clean_esnafnews_com(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div","style","span","button","blockquote","section","b","figure","figcaption","h2","h1","h3","ol"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
            
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p","style","span","button","blockquote","section","b","figure","figcaption","h2","h1","h3","ol"]):
        tag.attrs = {}  
    
    return str(soup)


def clean_donya_e_eqtesad_com(content_element):
    soup = BeautifulSoup(content_element, 'html.parser')
    
    
    #div ve p taglari bosdursa silir
    for tag in soup.find_all(["p", "div","style","span","button","blockquote","li","section","b","figure","figcaption","h2","h1","h3","h4","h5","h6","ol","td","table","ul","use","style","aside","article","i","strong"]):
        if not tag.text.strip() and not tag.find():  
            tag.decompose()
            
    #DIV VE P class adlari ve diger attributlari silir
    for tag in soup.find_all(["div", "p","style","span","button","blockquote","li","section","b","figure","figcaption","h2","h1","h3","h4","h5","h6","ol","td","table","ul","use","style","aside","article","i","strong"]):
        tag.attrs = {}  
    
    return str(soup)

