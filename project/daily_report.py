import psycopg2
import subprocess
from datetime import datetime

def generate_report():
    print("Məlumatlar toplanır, zəhmət olmasa gözləyin...\n")
    
    # 1. Cari Tarix
    today_date = datetime.now().strftime("%d.%m.%Y")
    
    # 2. Database məlumatlarını çəkmək
    try:
        conn = psycopg2.connect(
            host="192.168.0.203",
            dbname="scrape_db3",
            user="scrape_user",
            password="YaKRp92XMsoeCm4A"
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()));")
        db_size = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scraper_newsarticle;")
        total_news = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scraper_newsarticle WHERE DATE(created_at) = CURRENT_DATE;")
        today_news = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT ROUND(AVG(daily_count)) 
            FROM (
                SELECT DATE(created_at), COUNT(*) AS daily_count 
                FROM scraper_newsarticle 
                GROUP BY DATE(created_at)
            ) AS subquery;
        """)
        avg_news = int(cursor.fetchone()[0])
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"XƏTA: Verilənlər bazasına qoşulmaq mümkün olmadı: {e}")
        return



    # 4. Mount olunmuş Disk məlumatlarını dəqiq oxumaq
    disk_total, disk_used, disk_free = "Təyin olunmadı", "Təyin olunmadı", "Təyin olunmadı"
    try:
        df_output = subprocess.check_output(['df', '-h']).decode('utf-8')
        for line in df_output.splitlines():
            if "192.168.0.62:/mnt/storage/images" in line or "/home/rv/odin/project/media" in line:
                parts = line.split()
                # df -h çıxışında: [Filesystem, Size, Used, Avail, Use%, Mounted on]
                disk_total = parts[1].replace('G', ' gb')
                disk_used = parts[2].replace('G', ' gb')
                disk_free = parts[3].replace('G', ' gb')
                break
    except Exception as e:
        print(f"Disk məlumatlarını oxuyarkən xəta: {e}")

    # 5. Minlik ayırıcıları . (nöqtə) ilə formatlamaq
    def format_num(num):
        return f"{num:,}".replace(",", ".")

    # 6. Səliqəli Çap (Print)
    print("-" * 50)
    print("📊 GÜNLÜK EXCEL HESABATI")
    print("-" * 50)
    print(f"Date:\t\t\t{today_date}")
    print(f"db size:\t\t{db_size}")
    print(f"ümumi xəbər sayı:\t{format_num(total_news)}")
    print(f"bugünə xəbər sayı:\t{format_num(today_news)}")
    print(f"günlük ortalama:\t{format_num(avg_news)}")
    print(f"media disk ümumi:\t{disk_total}")
    print(f"media disk islenen:\t{disk_used}")
    print(f"media disk bos:\t\t{disk_free}")
    print("-" * 50)

if __name__ == "__main__":
    generate_report()
