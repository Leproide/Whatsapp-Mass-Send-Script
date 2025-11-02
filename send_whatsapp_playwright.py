# send_whatsapp_playwright.py
# Python + Playwright - invia messaggi WhatsApp Web
# Usa Destinatari.txt (uno per riga) e Messaggio.txt
# Attende il campo contenteditable dentro il footer (evita di scrivere nella barra di ricerca).
# Usa element_handle.evaluate(...) per inserire testo.

import os
import sys
import time
import random
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

BASE_DIR = Path.cwd()
RECIPIENTS_FILE = BASE_DIR / "Destinatari.txt"
MESSAGE_FILE    = BASE_DIR / "Messaggio.txt"
USER_DATA_DIR   = BASE_DIR / "whatsapp-profile"  # mantiene login
WAIT_FOR_SELECTOR_MS = 60000  # timeout attesa (ms)
NAV_WAIT_MS = 20000  # timeout navigazione (ms)

def read_recipients(path):
    if not path.exists():
        print(f"[ERR] File non trovato: {path}")
        sys.exit(1)
    raw_lines = [line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()]
    nums = []
    for original in raw_lines:
        if not original:
            continue
        digits = "".join(ch for ch in original if ch.isdigit())
        if 6 <= len(digits) <= 15:
            nums.append(digits)
        else:
            print(f"[WARN] Skipping invalid number (orig='{original}' -> digits='{digits}')")
    return nums

def read_message(path):
    if not path.exists():
        print(f"[ERR] File non trovato: {path}")
        sys.exit(1)
    msg = path.read_text(encoding="utf-8").strip()
    if not msg:
        print("[ERR] Messaggio vuoto")
        sys.exit(1)
    return msg

def find_footer_textbox(page):
    """
    Cerca il contenteditable della chat **dentro il footer** (evita la barra di ricerca).
    Ritorna element_handle oppure None.
    """
    try:
        # aspetta che il footer esista nella pagina della chat
        footer = page.wait_for_selector("footer", timeout=WAIT_FOR_SELECTOR_MS)
        if footer:
            # prova selettore più specifico dentro il footer
            # (div contenteditable direttamente figlio del footer o nelle sue sottosezioni)
            selectors = [
                "footer div[contenteditable='true']",
                "footer div[role='textbox'][contenteditable='true']",
                "div.copyable-area footer div[contenteditable='true']"
            ]
            for s in selectors:
                el = page.query_selector(s)
                if el:
                    return el
    except PlaywrightTimeoutError:
        return None
    return None

def fallback_textbox_search(page):
    """Fallback: cerca contenteditable generico ma assicurati sia visibile."""
    candidates = [
        'div[contenteditable="true"][data-tab]',
        'div[role="textbox"][contenteditable="true"]',
        'div[contenteditable="true"]'
    ]
    for sel in candidates:
        try:
            el = page.query_selector(sel)
            if el:
                # ulteriore controllo: è dentro la UI della chat? vero se esiste footer o header vicino
                return el
        except Exception:
            pass
    return None

def safe_insert_and_send(page, message):
    # 1) prova a trovare textbox dentro footer (robusto, evita la ricerca)
    textbox = find_footer_textbox(page)
    used_by = "footer" if textbox else "fallback"
    if not textbox:
        textbox = fallback_textbox_search(page)
    if not textbox:
        raise RuntimeError("Campo messaggio non trovato (né in footer né fallback).")

    # click + focus
    try:
        textbox.click(timeout=5000)
    except Exception:
        # se click fallisce, prova focus via evaluate
        try:
            textbox.evaluate("(el)=>el.focus()")
        except Exception:
            pass

    # Se il messaggio contiene newline, inserisci riga per riga e simula Shift+Enter
    if "\n" in message:
        parts = message.split("\n")  # mantiene anche eventuali righe vuote
        for idx, part in enumerate(parts):
            # inserisci la parte corrente
            try:
                # prova execCommand per inserire in modo corretto (genera input event)
                textbox.evaluate(
                    """(el, txt) => {
                        try {
                            el.focus();
                            document.execCommand('insertText', false, txt);
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                        } catch (e) {
                            // fallback minimale: append text node
                            el.appendChild(document.createTextNode(txt));
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    }""",
                    part
                )
            except Exception as ex:
                # ultima risorsa: usa keyboard.type (più lento ma funziona)
                print(f"[WARN] insert part evaluate() fallito, uso keyboard.type. Err: {ex}")
                try:
                    textbox.evaluate("(el)=>el.focus()")
                except Exception:
                    pass
                page.keyboard.type(part, delay=5)

            # se non è l'ultima parte, simula Shift+Enter per andare a capo
            if idx < len(parts) - 1:
                try:
                    page.keyboard.down("Shift")
                    page.keyboard.press("Enter")
                    page.keyboard.up("Shift")
                except Exception:
                    # in caso di fallimento, prova con evaluate: inserisci <br>
                    try:
                        textbox.evaluate("(el)=>{ el.appendChild(document.createElement('br')); el.dispatchEvent(new Event('input', { bubbles: true })); }")
                    except Exception:
                        pass

            # piccolo delay per lasciare al DOM il tempo di aggiornarsi
            page.wait_for_timeout(80)
    else:
        # inserimento testo tramite element_handle.evaluate (genera eventi)
        try:
            textbox.evaluate(
                """(el, msg) => {
                    try {
                        el.focus();
                        // posiziona caret alla fine
                        const selection = window.getSelection();
                        const range = document.createRange();
                        range.selectNodeContents(el);
                        range.collapse(false);
                        selection.removeAllRanges();
                        selection.addRange(range);
                        // inserimento sicuro
                        document.execCommand('insertText', false, msg);
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                    } catch (e) {
                        // fallback: set textContent e dispatch
                        el.textContent = msg;
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                }""",
                message
            )
        except Exception as ex:
            # ultima risorsa: usa keyboard.type (più lento ma funziona)
            print(f"[WARN] evaluate() fallito, uso keyboard.type. Err: {ex}")
            page.keyboard.type(message, delay=5)

    page.wait_for_timeout(250)

    # 2) prova a cliccare il bottone invia
    send_btn_selectors = [
        'footer button[data-testid="compose-btn-send"]',
        'footer span[data-icon="send"]',
        'button[data-testid="compose-btn-send"]',
        'span[data-icon="send"]',
        'button[aria-label*="Send"]',
        'button[aria-label*="Invia"]'
    ]
    clicked = False
    for sb in send_btn_selectors:
        try:
            btn = page.query_selector(sb)
            if btn:
                try:
                    btn.click()
                except Exception:
                    try:
                        btn.evaluate("(b)=>b.click()")
                    except Exception:
                        pass
                clicked = True
                break
        except Exception:
            pass

    if not clicked:
        # fallback: premi Enter (sembra il metodo più compatibile)
        page.keyboard.press("Enter")

def main():
    recipients = read_recipients(RECIPIENTS_FILE)
    message = read_message(MESSAGE_FILE)

    if not recipients:
        print("[ERR] Nessun destinatario valido trovato.")
        sys.exit(1)

    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser_context = p.chromium.launch_persistent_context(
            str(USER_DATA_DIR),
            headless=False,
            args=["--start-maximized"]
        )
        page = browser_context.new_page()
        page.goto("https://web.whatsapp.com", wait_until="domcontentloaded", timeout=NAV_WAIT_MS)
        print("Apri WhatsApp Web nella finestra del browser e completa il login se necessario.")
        try:
            page.wait_for_selector('div[contenteditable="true"], div[role="textbox"]', timeout=120000)
            print("WhatsApp Web pronto.")
        except PlaywrightTimeoutError:
            print("[WARN] Timeout: WhatsApp Web potrebbe non essere loggato. Se non l'hai fatto, esegui il login nel browser aperto.")

        for num in recipients:
            try:
                print(f"[INFO] Navigo a: {num}")
                send_url = f"https://web.whatsapp.com/send?phone={num}&app_absent=0"
                page.goto(send_url, wait_until="domcontentloaded", timeout=NAV_WAIT_MS)

                # aspetta che la chat si carichi: header o footer
                try:
                    page.wait_for_selector("header", timeout=10000)
                except PlaywrightTimeoutError:
                    # ok, non critico, prosegui e lascia che safe_insert_and_send faccia timeout specifico
                    pass

                safe_insert_and_send(page, message)
                print(f"[OK] Inviato a {num}")
            except Exception as e:
                print(f"[ERR] Errore con {num}: {e}")

            wait_s = random.uniform(2.0, 6.0)
            time.sleep(wait_s)

        print("Tutti i destinatari processati. Chiudo browser fra 3s.")
        time.sleep(3)
        browser_context.close()

if __name__ == "__main__":
    main()
