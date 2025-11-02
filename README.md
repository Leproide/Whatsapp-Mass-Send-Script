# Whatsapp Mass Send Script

**Python + Playwright** script for bulk sending messages via **WhatsApp Web**.

### 📦 How it works
- Uses `Destinatari.txt` — one phone number per line (digits only).  
- Uses `Messaggio.txt` — message content to send (supports multiline).  
- Waits for the **chat message box inside the footer**, avoiding the search bar.  
- Inserts text using `element_handle.evaluate(...)` for reliable input and event dispatch.  
- Each contact is opened, the message is sent, and the script waits a few seconds before continuing.

### ⚙️ Files
- `send_whatsapp_playwright.py` → the main script.  
- `Send.bat` → auto-installs **Python** (if missing) and required dependencies before running the script.  
- `requirements.txt` → contains the dependency list (`playwright`).

### 🧠 Notes
- First run will open **WhatsApp Web** and ask you to scan the QR code.  
- Login data is stored in the `whatsapp-profile` folder for persistence.  
- Compatible with Python ≥ 3.8 and Playwright ≥ 1.30.

---

### ⚠️ Warning
This script performs automated message sending.  
**WhatsApp may temporarily or permanently ban your account** if it detects automation or spam-like activity.  
Use it responsibly and avoid sending unsolicited or bulk messages to unknown contacts.

Keep in mind that **WhatsApp officially sells its own Business API** for controlled and approved automation use.  
Using unofficial automation tools like this one is **not endorsed by WhatsApp** and may violate their Terms of Service.

---

> 🧩 For educational or personal automation use only. Respect WhatsApp’s usage policies.
