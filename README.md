# ✈️ TravelPlanner

### A Flask-based web app that makes trip planning collaborative and fun. Create trips that look like plane tickets, drag & drop activities into your itinerary, discover nearby places with Google Places powered by your preselected interests that help groups plan more efficiently.

---

## Core Features

- 🛫 **Dashboard (Ticket Cards)**
  - Trips are displayed like plane tickets.
  - Click a ticket to open **Trip Details**.

- 📅 **Trip Details → Possible Activities**
  - Browse **possible activities** for the destination.
  - **Drag & drop** activities into your day-by-day itinerary.
  - Click any activity to open a **details modal** with:
    - ⭐ **Reviews** (what others thought)
    - 👍 **Voting** (help the group prioritize)
    - 🖼️ **Images** (gallery)

- 📊 **Reservation Likely + Group Consensus**
  - A widget that displays activities that need booking.
  - **Group Consensus score** (derived from votes) helps teams align faster.

- 🎯 **Interests**
  - Preselect categories (e.g., food, museums, nightlife).
  - These interests drive the **Nearby** search.

- 🗺️ **Nearby (Google Places + Map)**
  - Uses **Google Places API** filtered by your Interests.
  - Shows a **map** centered on your input location to visualize **distance**.
  - (Unlike activity details) Nearby focuses on **map + distance**, not reviews.

---

## 🛠 Tech Stack

- **Backend:** Python, Flask, SQLAlchemy  
- **Frontend:** HTML, CSS, JavaScript  
- **Database:** SQLite (dev) → PostgreSQL (planned)  
- **APIs:** Google Maps JavaScript API, Google Places API

---

## 📸 Screenshots

- **Dashboard** <img width="1900" height="800" alt="Screenshot 2025-08-23 183510" src="https://github.com/user-attachments/assets/39d1f12e-a782-4c1e-8200-7c4b70c3419d" />
- **Trip Details** <img width="960" height="295" alt="Untitled presentation" src="https://github.com/user-attachments/assets/a5f4b8a4-df9e-498f-baa5-610c7dc6d5fb" />
- **Trip Details Description** <img width="1900" height="800" alt="Screenshot 2025-08-23 184346" src="https://github.com/user-attachments/assets/3281af3c-ded9-4128-9e21-cf12d482c70e" />
- **Nearby** <img width="1900" height="800" alt="Screenshot 2025-08-23 184049" src="https://github.com/user-attachments/assets/059c4f40-217d-4fab-aef7-8775adc72e48" />
- **Nearby Location Details** <img width="1900" height="800" alt="Screenshot 2025-08-23 184137" src="https://github.com/user-attachments/assets/9e05237d-32da-4eae-8596-d0326979ed96" />



