from rich.console import Console
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

console = Console()

class BrowserManager:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver = None
        self.last_response_body = None

    def start(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Enable Performance Logging for Network
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # We will use CDP to intercept responses more reliably if needed,
        # but for simple capture, Performance Logs + CDP getResponseBody is effective.
        # Alternatively, we can just poll performance logs.
        # Let's stick to polling performance logs which is standard for Selenium.

    def navigate(self, url: str):
        console.print(f"[bold blue]Navigating to:[/bold blue] {url}")
        self.driver.get(url)

    def send_message(self, selector_input: str, selector_send: str, message: str):
        try:
            # Clear previous captured request logic if any (optional)
            self.last_response_body = None
            
            # Find input
            wait = WebDriverWait(self.driver, 10)
            input_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector_input)))
            input_box.clear()
            input_box.send_keys(message)
            
            # Click send
            send_btn = self.driver.find_element(By.CSS_SELECTOR, selector_send)
            send_btn.click()
            
            console.print(f"[green]Sent:[/green] {message}")
            
        except Exception as e:
            console.print(f"[bold red]Error sending message:[/bold red] {e}")

    def capture_last_network_response(self, timeout=10) -> str:
        """
        Scans network logs for the latest XHR/Fetch response containing text.
        Returns the response body.
        """
        console.print(f"[dim]Listening for Network Response (Max {timeout}s)...[/dim]")
        
        # Wait up to 'timeout' seconds for a relevant response
        start_time = time.time()
        while time.time() - start_time < timeout:
            logs = self.driver.get_log("performance")
            
            # Reverse logs to find the newest response first
            for entry in reversed(logs):
                message = json.loads(entry["message"])["message"]
                
                # We care about Network.responseReceived
                if message["method"] == "Network.responseReceived":
                    resp_url = message["params"]["response"]["url"]
                    request_id = message["params"]["requestId"]
                    mime_type = message["params"]["response"]["mimeType"]
                    
                    # Filter for likely chat APIs (json/text) and ignore statics
                    if "json" in mime_type or "text" in mime_type:
                        # Skip own interactions or noise if needed
                        if "chat" in resp_url or "completion" in resp_url: # Heuristic
                            try:
                                # Use CDP to get the actual body
                                cdp_result = self.driver.execute_cdp_cmd(
                                    "Network.getResponseBody", 
                                    {"requestId": request_id}
                                )
                                body = cdp_result.get("body", "")
                                if body:
                                    console.print(f"[blue]Captured Network Body:[/blue] {body[:100]}...")
                                    return body
                            except Exception:
                                # Sometimes body is not available or request failed
                                continue
            
            time.sleep(0.5)
            
        return ""

    def auto_discover_chat_elements(self):
        """
        Attempts to automatically find the chat input and send button.
        Returns (input_selector, send_selector) or raises Exception if not found.
        """
        console.print("[dim]Auto-discovering chat elements...[/dim]")
        
        # Heuristics for Input
        input_candidates = [
            "input[type='text']",
            "textarea",
            "input[placeholder*='message']",
            "input[placeholder*='chat']",
            "#message-input",
            ".chat-input"
        ]
        
        found_input = None
        for sel in input_candidates:
            try:
                elem = self.driver.find_element(By.CSS_SELECTOR, sel)
                if elem.is_displayed():
                    found_input = sel
                    console.print(f"[green]Found Input:[/green] {sel}")
                    break
            except:
                continue
                
        if not found_input:
            raise Exception("Could not auto-discover chat input. Please specify --input.")
            
        # Heuristics for Send Button
        btn_candidates = [
            "button[type='submit']",
            "button",
            "input[type='submit']",
            ".send-btn",
            "#send-btn",
            "[aria-label='Send']",
            "svg" # Sometimes it's just an icon
        ]
        
        found_btn = None
        for sel in btn_candidates:
            try:
                # Find all matching, check if near input or contains 'Send' text
                elems = self.driver.find_elements(By.CSS_SELECTOR, sel)
                for elem in elems:
                    if not elem.is_displayed():
                        continue
                        
                    # Basic checks
                    text = elem.text.lower()
                    if "send" in text or "chat" in text or "submit" in text:
                        found_btn = sel # Simply return the selector that matched
                        break
                        
                    # If just a generic button, verify it's not some other nav
                    # This is rough, but for CTF/demos usually specific enough
                    if sel == "button":
                         found_btn = "button" # Fallback
                
                if found_btn:
                    console.print(f"[green]Found Button:[/green] {found_btn}")
                    break
            except:
                continue
                
        if not found_btn:
            console.print("[yellow]Warning:[/yellow] Could not clearly identify send button. Using 'input' + Enter key strategy if possible.")
            found_btn = None # Attacker will handle this by sending \n
            
        return found_input, found_btn

    def close(self):
        if self.driver:
            self.driver.quit()
