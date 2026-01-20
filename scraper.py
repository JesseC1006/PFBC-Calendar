import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from dateutil import parser
from datetime import timedelta

CALENDAR_URL = "https://fbweb.pa.gov/calendar/"
OUTPUT_FILE = "pfbc_events.ics"

def scrape_pfbc_calendar():
    response = requests.get(CALENDAR_URL, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    calendar = Calendar()

    events = soup.select("div.views-row")

    for ev in events:
        try:
            title_el = ev.select_one("h3, h2")
            date_el = ev.select_one(".date")
            link_el = ev.find("a", href=True)

            if not title_el or not date_el:
                continue

            title = title_el.get_text(strip=True)
            date_text = date_el.get_text(" ", strip=True)

            start = parser.parse(date_text, fuzzy=True)
            end = start + timedelta(hours=2)

            event = Event()
            event.name = title
            event.begin = start
            event.end = end
            event.url = link_el["href"] if link_el else CALENDAR_URL
            event.description = "PA Fish & Boat Commission Event"

            calendar.events.add(event)

        except Exception as e:
            print(f"Skipped event: {e}")

    return calendar

if __name__ == "__main__":
    cal = scrape_pfbc_calendar()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.writelines(cal)

