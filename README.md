# Whatsapp Mass Send Script

**Python + Playwright** tool for sending messages in bulk via **WhatsApp Web**.

### 📦 Overview
- Internal-use automation tool — provided *as-is* without guarantees.  
- Uses **WhatsApp Web** to send text messages automatically to a list of recipients.  
- Currently supports **text-only messages** (no images, videos, or file attachments yet).  
- Community **contributions and improvements are welcome**.

### ⚙️ How it works
- `Destinatari.txt` → one phone number per line (digits only).  
- `Messaggio.txt` → message body to send (multiline supported).  
- Waits for the **message input box inside the footer**, avoiding false matches like the search bar.  
- Inserts text safely using `element_handle.evaluate(...)` to simulate user typing and trigger events.  
- Each recipient is opened in sequence, message sent, and the script pauses briefly between sends.

### 🧩 Files
- `send_whatsapp_playwright.py` → main script.  
- `Send.bat` → automatically installs **Python** (if missing) and dependencies before execution.  
- `requirements.txt` / `dipendenze.txt` → dependency list (`playwright`).

### 🧠 Notes
- On first run, a browser window will open — scan the QR code to log in to WhatsApp Web.  
- Login data is saved under `whatsapp-profile` to persist sessions between runs.  
- Works with Python ≥ 3.8 and Playwright ≥ 1.30.

### ⚠️ Important notice
This script performs **automated message sending**, which may violate WhatsApp’s Terms of Service.  
**WhatsApp may restrict or ban accounts** if automated behavior or mass messaging is detected.  
Use only for legitimate, internal, or educational purposes. Avoid spam or unsolicited messages.

> For approved automation and message delivery, WhatsApp provides its **official Business API**.  
> This tool is **not affiliated with or endorsed by WhatsApp** in any way.

---

🧩 *Developed for internal use — released “as-is”.  
Contributions, fixes, and feature extensions (like media attachments) are welcome!*
