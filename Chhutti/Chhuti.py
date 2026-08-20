import io
import threading
import tkinter as tk
import customtkinter as ctk
import feedparser
import pdfplumber
from plyer import notification  # Native OS Notifications
import requests

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class DehradunWeatherDashboard(ctk.CTk):

  def __init__(self):
    super().__init__()

    self.title("Dehradun Weather Risk & DM Holiday Dashboard")
    self.geometry("950x720")
    self.resizable(False, False)

    self.grid_columnconfigure((0, 1), weight=1)
    self.grid_rowconfigure(2, weight=1)

    # ------------------ TOP HEADER ------------------
    self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
    self.header_frame.grid(
        row=0, column=0, columnspan=2, padx=20, pady=(15, 10), sticky="ew"
    )

    self.title_label = ctk.CTkLabel(
        self.header_frame,
        text="Dehradun Weather Risk & DM Holiday Dashboard",
        font=ctk.CTkFont(size=22, weight="bold"),
    )
    self.title_label.pack(side="left")

    self.refresh_btn = ctk.CTkButton(
        self.header_frame,
        text="↻ Refresh Data",
        width=120,
        command=self.start_async_data_fetch,
    )
    self.refresh_btn.pack(side="right")

    # ------------------ LEFT CARD: METRICS ------------------
    self.imd_card = ctk.CTkFrame(self, corner_radius=10)
    self.imd_card.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="nsew")

    ctk.CTkLabel(
        self.imd_card,
        text="HYBRID METEOROLOGICAL DATA",
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color="#A0A0A0",
    ).pack(anchor="w", padx=15, pady=(15, 5))

    self.lbl_alert_source = self.create_info_row(
        self.imd_card, "Source Mode:", "IMD PDF + OpenMeteo"
    )
    self.lbl_precip = self.create_info_row(
        self.imd_card, "Expected Rain:", "Calculating..."
    )
    self.lbl_intensity = self.create_info_row(
        self.imd_card, "Max Intensity:", "Calculating..."
    )

    self.badge_alert = ctk.CTkButton(
        self.imd_card,
        text="FETCHING ALERT LEVEL",
        state="disabled",
        fg_color="#333333",
        text_color_disabled="#FFFFFF",
        font=ctk.CTkFont(weight="bold"),
    )
    self.badge_alert.pack(padx=15, pady=15, fill="x")

    # ------------------ RIGHT CARD: HOLIDAY ENGINE ------------------
    self.predictor_card = ctk.CTkFrame(self, corner_radius=10)
    self.predictor_card.grid(
        row=1, column=1, padx=(10, 20), pady=10, sticky="nsew"
    )

    ctk.CTkLabel(
        self.predictor_card,
        text="HOLIDAY PREDICTION ENGINE",
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color="#A0A0A0",
    ).pack(anchor="w", padx=15, pady=(15, 5))

    self.lbl_chance = self.create_info_row(
        self.predictor_card,
        "Holiday Chance:",
        "--%",
        font_size=18,
        bold=True,
    )
    self.lbl_dm_status = self.create_info_row(
        self.predictor_card, "DM Circular:", "Checking feeds..."
    )
    self.lbl_advisory = self.create_info_row(
        self.predictor_card, "Advisory:", "Analyzing forecast..."
    )

    # ------------------ BOTTOM CARD: NEWS FEEDS ------------------
    self.feed_card = ctk.CTkFrame(self, corner_radius=10)
    self.feed_card.grid(
        row=2,
        column=0,
        columnspan=2,
        padx=20,
        pady=(10, 20),
        sticky="nsew",
    )

    ctk.CTkLabel(
        self.feed_card,
        text="LIVE SCRAPED DM ANNOUNCEMENTS & NEWS FEEDS",
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color="#A0A0A0",
    ).pack(anchor="w", padx=15, pady=(10, 5))

    self.feed_textbox = ctk.CTkTextbox(
        self.feed_card, font=ctk.CTkFont(family="Consolas", size=12)
    )
    self.feed_textbox.pack(padx=15, pady=(0, 15), fill="both", expand=True)

    self.start_async_data_fetch()

  def create_info_row(
      self, parent, label_text, default_val, font_size=12, bold=False
  ):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x", padx=15, pady=4)

    lbl = ctk.CTkLabel(
        frame, text=label_text, font=ctk.CTkFont(size=12), text_color="#888888"
    )
    lbl.pack(side="left")

    weight = "bold" if bold else "normal"
    val = ctk.CTkLabel(
        frame,
        text=default_val,
        font=ctk.CTkFont(size=font_size, weight=weight),
        wraplength=260,
        justify="left",
    )
    val.pack(side="right")
    return val

  def send_desktop_notification(self, title, message):
    """Triggers a native Windows/macOS desktop pop-up notification."""
    try:
      notification.notify(
          title=title,
          message=message,
          app_name="Dehradun Weather Alert",
          timeout=10,  # Notification stays for 10 seconds
      )
    except Exception as e:
      print(f"Notification Error: {e}")

  def start_async_data_fetch(self):
    self.refresh_btn.configure(state="disabled", text="Updating...")
    threading.Thread(target=self.fetch_and_update_gui, daemon=True).start()

  def fetch_accurate_imd_pdf_warning(self):
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
            return (
                "RED ALERT",
                "Extremely heavy rain / severe landslide threat.",
            )
          elif (
              "heavy to very heavy" in full_text or "orange alert" in full_text
          ):
            return "ORANGE ALERT", "Heavy to very heavy rainfall forecast."
          elif "heavy rain" in full_text or "yellow alert" in full_text:
            return (
                "YELLOW ALERT",
                "Isolated heavy rainfall / thunderstorm warning.",
            )
    except Exception as e:
      print(f"PDF Fetch Fallback: {e}")

    return "GREEN (NO ALERT)", "Normal light or moderate rain expected."

  def fetch_openmeteo_precipitation(self):
    url = "https://api.open-meteo.com/v1/forecast?latitude=30.3165&longitude=78.0322&hourly=precipitation,rain&forecast_days=2&timezone=Asia%2FKolkata"
    try:
      resp = requests.get(url, timeout=5).json()
      tomorrow_rain = sum(resp["hourly"]["precipitation"][24:48])
      max_hourly = max(resp["hourly"]["precipitation"][24:48])
      return round(tomorrow_rain, 1), round(max_hourly, 1)
    except Exception as e:
      print(f"Open-Meteo Fetch Error: {e}")
      return 0.0, 0.0

  def scrape_dm_and_news_updates(self):
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

  def fetch_and_update_gui(self):
    alert_level, warning_desc = self.fetch_accurate_imd_pdf_warning()
    total_mm, max_mm_hr = self.fetch_openmeteo_precipitation()
    news_feed, dm_order_found = self.scrape_dm_and_news_updates()

    weather_data = {
        "alert": alert_level,
        "warning": warning_desc,
        "total_mm": f"{total_mm} mm",
        "max_mm_hr": f"{max_mm_hr} mm/hr",
        "raw_mm": total_mm,
    }

    self.after(
        0,
        lambda: self.render_ui(weather_data, news_feed, dm_order_found),
    )

  def render_ui(self, weather_data, news_feed, dm_order_found):
    self.lbl_precip.configure(text=weather_data["total_mm"])
    self.lbl_intensity.configure(text=weather_data["max_mm_hr"])

    alert_str = weather_data["alert"]

    if "RED" in alert_str or weather_data["raw_mm"] > 65.0:
      color = "#E74C3C"
      base_prob = 90
    elif "ORANGE" in alert_str or weather_data["raw_mm"] > 35.0:
      color = "#E67E22"
      base_prob = 65
    elif "YELLOW" in alert_str or weather_data["raw_mm"] > 10.0:
      color = "#F1C40F"
      base_prob = 30
    else:
      color = "#2ECC71"
      base_prob = 5

    if dm_order_found:
      final_prob = 98
      dm_text = "CONFIRMED ORDER DETECTED"
      advisory = (
          "High Probability: DM School closure notice detected in local"
          " bulletins."
      )

      # Trigger push notification on official order
      self.send_desktop_notification(
          title="⚠️ Dehradun DM Holiday Detected!",
          message=(
              "Local news feeds confirm a school closure / holiday order for"
              " Dehradun tomorrow."
          ),
      )
    else:
      final_prob = base_prob
      dm_text = "No Explicit Order Yet"
      advisory = (
          "Regular operations unless local IMD warnings escalate overnight."
      )

      # Trigger push notification on severe alert warnings
      if "ORANGE" in alert_str or "RED" in alert_str:
        self.send_desktop_notification(
            title=f"⚠️ Dehradun Weather Alert: {alert_str}",
            message=(
                f"Severe rainfall forecast ({weather_data['total_mm']})."
                f" Predicted holiday chance: {final_prob}%"
            ),
        )

    self.badge_alert.configure(text=alert_str, fg_color=color)
    self.lbl_chance.configure(text=f"{final_prob}%", text_color=color)
    self.lbl_dm_status.configure(
        text=dm_text, text_color="#2ECC71" if dm_order_found else "#FFFFFF"
    )
    self.lbl_advisory.configure(text=advisory)

    self.feed_textbox.delete("1.0", tk.END)
    self.feed_textbox.insert(tk.END, news_feed)

    self.refresh_btn.configure(state="normal", text="↻ Refresh Data")


if __name__ == "__main__":
  app = DehradunWeatherDashboard()
  app.mainloop()