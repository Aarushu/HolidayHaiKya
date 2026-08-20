import io
import requests
import feedparser
import pdfplumber

def fetch_accurate_imd_pdf_warning():
    pdf_url = "https://mausam.imd.gov.in/dehradun/mcdata/DehradunCityForecast.pdf"
    try:
        response = requests.get(pdf_url, timeout=8)
        if response.status_code == 200:
            with pdfplumber.open(io.BytesIO(response.content)) as pdf:
                full_text = ""
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        full_text += extracted.lower() + "\n"

                if "extremely heavy" in full_text or "red alert" in full_text:
                    return "RED ALERT", "Extremely heavy rain / severe landslide threat."
                elif "heavy to very heavy" in full_text or "orange alert" in full_text:
                    return "ORANGE ALERT", "Heavy to very heavy rainfall forecast."
                elif "heavy rain" in full_text or "yellow alert" in full_text:
                    return "YELLOW ALERT", "Isolated heavy rainfall / thunderstorm warning."
    except Exception as e:
        print(f"PDF Fetch Fallback: {e}")

    return "GREEN (NO ALERT)", "Normal light or moderate rain expected."


def fetch_openmeteo_precipitation():
    url = "https://api.open-meteo.com/v1/forecast?latitude=30.3165&longitude=78.0322&hourly=precipitation,rain&forecast_days=2&timezone=Asia%2FKolkata"
    try:
        resp = requests.get(url, timeout=5).json()
        # Calculate tomorrow's rain and max hourly intensity
        tomorrow_rain = sum(resp["hourly"]["precipitation"][24:48])
        max_hourly = max(resp["hourly"]["precipitation"][24:48])
        return round(tomorrow_rain, 1), round(max_hourly, 1)
    except Exception as e:
        print(f"Open-Meteo Fetch Error: {e}")
        return 0.0, 0.0


def scrape_dm_and_news_updates():
    queries = [
        "Dehradun+DM+school+holiday",
        "Uttarakhand+rain+alert+school+closed",
    ]
    scraped_headlines = []
    official_order_detected = False

    for q in queries:
        rss_url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(rss_url)

        for entry in feed.entries[:4]:
            title = entry.title
            scraped_headlines.append(f"• {title}")

            lower_title = title.lower()
            if "dehradun" in lower_title and any(
                k in lower_title for k in ["holiday", "closed", "closure", "shut"]
            ):
                official_order_detected = True

    headline_text = (
        "\n".join(scraped_headlines)
        if scraped_headlines
        else "No recent local news announcements found."
    )
    return headline_text, official_order_detected