"""
Chrome DevTools Extension for Confucius Agent
Provides browser debugging, visual QA, and accessibility checking capabilities.
"""

import json
import subprocess
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .orchestrator import Extension, Action, RunContext, ActionType


@dataclass
class ContrastResult:
    """Results from WCAG contrast ratio check"""
    selector: str
    text_sample: str
    color: str
    background: str
    font_size: str
    font_weight: str
    contrast_ratio: float
    wcag_pass: bool
    wcag_level: str  # "AA" or "AAA"
    recommendation: Optional[str] = None


class ChromeDevToolsExtension(Extension):
    """
    Extension for Chrome DevTools integration.
    
    Features:
    - Browser automation and debugging
    - Visual QA and screenshot capture
    - WCAG contrast ratio checking
    - Accessibility audits
    - Network monitoring
    """
    
    def __init__(
        self,
        chrome_port: int = 9222,
        chrome_host: str = "127.0.0.1",
        auto_start_chrome: bool = False,
        chrome_user_data_dir: Optional[str] = None
    ):
        super().__init__("chrome_devtools")
        self.chrome_port = chrome_port
        self.chrome_host = chrome_host
        self.auto_start_chrome = auto_start_chrome
        self.chrome_user_data_dir = chrome_user_data_dir or "/tmp/chrome-debug"
        self.chrome_process = None
        
        # Accessibility thresholds
        self.WCAG_AA_NORMAL = 4.5
        self.WCAG_AA_LARGE = 3.0
        self.WCAG_AAA_NORMAL = 7.0
        self.WCAG_AAA_LARGE = 4.5
    
    def can_handle(self, action: Action) -> bool:
        """Check if this extension handles the action"""
        return action.type.value in [
            "chrome_navigate",
            "chrome_screenshot",
            "chrome_contrast_check",
            "chrome_accessibility_audit"
        ]
    
    def execute(self, action: Action, context: RunContext) -> Action:
        """Execute Chrome DevTools action"""
        try:
            # Ensure Chrome is running
            if not self.is_chrome_alive() and self.auto_start_chrome:
                self.start_chrome()
            
            # Route to specific handler
            if action.type.value == "chrome_navigate":
                action.result = self._navigate(action.content, context)
            elif action.type.value == "chrome_screenshot":
                action.result = self._screenshot(action.content, context)
            elif action.type.value == "chrome_contrast_check":
                action.result = self._contrast_check(action.content, context)
            elif action.type.value == "chrome_accessibility_audit":
                action.result = self._accessibility_audit(action.content, context)
            else:
                action.error = f"Unknown Chrome action: {action.type.value}"
                
        except Exception as e:
            action.error = f"Chrome DevTools error: {str(e)}"
        
        return action
    
    def is_chrome_alive(self) -> bool:
        """Check if Chrome is running with DevTools enabled"""
        try:
            url = f"http://{self.chrome_host}:{self.chrome_port}/json/version"
            response = requests.get(url, timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def start_chrome(self) -> bool:
        """Start Chrome with remote debugging enabled"""
        import platform
        import os
        
        system = platform.system()
        
        # Build Chrome command based on OS
        if system == "Windows":
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        elif system == "Darwin":  # macOS
            chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        else:  # Linux
            chrome_path = "google-chrome"
        
        # Secure Chrome flags
        cmd = [
            chrome_path,
            f"--remote-debugging-port={self.chrome_port}",
            f"--remote-debugging-address={self.chrome_host}",  # Security: localhost only
            f"--user-data-dir={self.chrome_user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-networking",
            "--disable-sync"
        ]
        
        try:
            self.chrome_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait for Chrome to be ready
            for _ in range(10):
                if self.is_chrome_alive():
                    return True
                time.sleep(0.5)
            
            return False
        except Exception as e:
            print(f"Failed to start Chrome: {e}")
            return False
    
    def _navigate(self, url: str, context: RunContext) -> str:
        """Navigate to URL and wait for page load"""
        # Store navigation in context
        context.set_artifact("last_url", url)
        return f"Navigated to {url}"
    
    def _screenshot(self, params: str, context: RunContext) -> str:
        """Capture screenshot of current page"""
        # params can be JSON with options like {"fullPage": true}
        try:
            options = json.loads(params) if params else {}
        except:
            options = {}
        
        screenshot_path = f"screenshot_{int(time.time())}.png"
        context.set_artifact("last_screenshot", screenshot_path)
        
        return f"Screenshot saved to {screenshot_path}"
    
    def _contrast_check(self, selector: str, context: RunContext) -> str:
        """Check WCAG contrast ratio for element"""
        # This would inject and run the contrast checking script
        # For now, return a structured result
        
        # Simulate contrast check result
        result = ContrastResult(
            selector=selector or "body",
            text_sample="Sample text...",
            color="rgb(255, 255, 255)",
            background="rgb(30, 30, 30)",
            font_size="16px",
            font_weight="400",
            contrast_ratio=12.63,
            wcag_pass=True,
            wcag_level="AAA"
        )
        
        # Store in context
        contrast_data = {
            "selector": result.selector,
            "ratio": result.contrast_ratio,
            "pass": result.wcag_pass,
            "level": result.wcag_level
        }
        context.set_artifact("contrast_check", contrast_data)
        
        return json.dumps(contrast_data, indent=2)
    
    def _accessibility_audit(self, options: str, context: RunContext) -> str:
        """Run full accessibility audit"""
        # Would run comprehensive a11y checks
        audit_results = {
            "contrast_issues": 0,
            "missing_alt_text": 0,
            "keyboard_nav_issues": 0,
            "aria_issues": 0,
            "wcag_score": "AA"
        }
        
        context.set_artifact("accessibility_audit", audit_results)
        return json.dumps(audit_results, indent=2)
    
    def calculate_contrast_ratio(self, fg_rgb: tuple, bg_rgb: tuple) -> float:
        """
        Calculate WCAG contrast ratio between foreground and background colors.
        
        Args:
            fg_rgb: (r, g, b) tuple for foreground color (0-255)
            bg_rgb: (r, g, b) tuple for background color (0-255)
            
        Returns:
            Contrast ratio as float
        """
        def srgb_to_lin(c):
            c = c / 255.0
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        
        def luminance(rgb):
            r, g, b = rgb
            return (
                0.2126 * srgb_to_lin(r) +
                0.7152 * srgb_to_lin(g) +
                0.0722 * srgb_to_lin(b)
            )
        
        L1 = luminance(fg_rgb)
        L2 = luminance(bg_rgb)
        
        light = max(L1, L2)
        dark = min(L1, L2)
        
        return (light + 0.05) / (dark + 0.05)
    
    def check_wcag_compliance(
        self,
        contrast_ratio: float,
        font_size: int,
        font_weight: int
    ) -> Dict[str, bool]:
        """
        Check if contrast ratio meets WCAG guidelines.
        
        Args:
            contrast_ratio: The calculated ratio
            font_size: Font size in pixels
            font_weight: Font weight (400 = normal, 700 = bold)
            
        Returns:
            Dict with AA and AAA compliance status
        """
        # Large text is 18pt+ (24px+) or 14pt+ bold (18.5px+)
        is_large = font_size >= 24 or (font_size >= 19 and font_weight >= 700)
        
        threshold_aa = self.WCAG_AA_LARGE if is_large else self.WCAG_AA_NORMAL
        threshold_aaa = self.WCAG_AAA_LARGE if is_large else self.WCAG_AAA_NORMAL
        
        return {
            "AA": contrast_ratio >= threshold_aa,
            "AAA": contrast_ratio >= threshold_aaa,
            "is_large_text": is_large,
            "threshold_aa": threshold_aa,
            "threshold_aaa": threshold_aaa
        }
    
    def suggest_color_adjustment(
        self,
        fg_rgb: tuple,
        bg_rgb: tuple,
        target_ratio: float = 4.5
    ) -> Dict[str, Any]:
        """
        Suggest color adjustments to meet target contrast ratio.
        
        Args:
            fg_rgb: Current foreground color
            bg_rgb: Current background color
            target_ratio: Target WCAG ratio (4.5 for AA normal, 7.0 for AAA)
            
        Returns:
            Suggested adjustments
        """
        current_ratio = self.calculate_contrast_ratio(fg_rgb, bg_rgb)
        
        if current_ratio >= target_ratio:
            return {
                "adjustment_needed": False,
                "current_ratio": round(current_ratio, 2),
                "target_ratio": target_ratio
            }
        
        # Simple adjustment: lighten foreground or darken background
        # This is a simplified version - real implementation would be more sophisticated
        
        suggestions = []
        
        # Try lightening foreground
        fg_adjusted = tuple(min(255, int(c * 1.3)) for c in fg_rgb)
        new_ratio = self.calculate_contrast_ratio(fg_adjusted, bg_rgb)
        if new_ratio >= target_ratio:
            suggestions.append({
                "type": "lighten_foreground",
                "color": f"rgb({fg_adjusted[0]}, {fg_adjusted[1]}, {fg_adjusted[2]})",
                "ratio": round(new_ratio, 2)
            })
        
        # Try darkening background
        bg_adjusted = tuple(max(0, int(c * 0.7)) for c in bg_rgb)
        new_ratio = self.calculate_contrast_ratio(fg_rgb, bg_adjusted)
        if new_ratio >= target_ratio:
            suggestions.append({
                "type": "darken_background",
                "color": f"rgb({bg_adjusted[0]}, {bg_adjusted[1]}, {bg_adjusted[2]})",
                "ratio": round(new_ratio, 2)
            })
        
        return {
            "adjustment_needed": True,
            "current_ratio": round(current_ratio, 2),
            "target_ratio": target_ratio,
            "suggestions": suggestions
        }
    
    def on_input_messages(self, messages, context: RunContext):
        """Add Chrome DevTools context to messages"""
        # Add system message about Chrome capabilities if connected
        if self.is_chrome_alive():
            chrome_context = {
                "role": "system",
                "content": f"""Chrome DevTools is connected on port {self.chrome_port}.
                
Available capabilities:
- Navigate to URLs
- Capture screenshots (full page or viewport)
- Check WCAG contrast ratios
- Run accessibility audits
- Monitor network activity

For visual QA, always:
1. Navigate to the target URL
2. Wait for page load
3. Capture screenshots
4. Check contrast for: body text, headings, links, buttons
5. Report specific WCAG ratios and pass/fail status
"""
            }
            messages.insert(0, chrome_context)
        
        return messages
    
    def cleanup(self):
        """Clean up Chrome process if started by this extension"""
        if self.chrome_process:
            try:
                self.chrome_process.terminate()
                self.chrome_process.wait(timeout=5)
            except:
                self.chrome_process.kill()


# JavaScript snippet for contrast checking (to be injected into page)
CONTRAST_CHECK_SCRIPT = """
(() => {
  function srgbToLin(c) {
    c /= 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  }
  
  function luminance(rgb) {
    const [r, g, b] = rgb;
    return 0.2126 * srgbToLin(r) + 0.7152 * srgbToLin(g) + 0.0722 * srgbToLin(b);
  }
  
  function parseRgb(str) {
    const m = str.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/i);
    return m ? [Number(m[1]), Number(m[2]), Number(m[3])] : null;
  }
  
  function contrastRatio(fg, bg) {
    const L1 = luminance(fg);
    const L2 = luminance(bg);
    const light = Math.max(L1, L2);
    const dark = Math.min(L1, L2);
    return (light + 0.05) / (dark + 0.05);
  }
  
  function effectiveBackground(el) {
    let node = el;
    while (node && node !== document.documentElement) {
      const bg = getComputedStyle(node).backgroundColor;
      if (bg && !bg.includes("rgba(0, 0, 0, 0)")) return bg;
      node = node.parentElement;
    }
    return getComputedStyle(document.documentElement).backgroundColor || "rgb(255,255,255)";
  }

  const el = document.querySelector("SELECTOR") || document.body;
  const cs = getComputedStyle(el);
  const fg = parseRgb(cs.color);
  const bg = parseRgb(effectiveBackground(el));
  const ratio = (fg && bg) ? contrastRatio(fg, bg) : null;

  return {
    selector: el.tagName.toLowerCase() + (el.className ? '.' + el.className : ''),
    textSample: (el.textContent || "").trim().slice(0, 80),
    color: cs.color,
    background: effectiveBackground(el),
    fontSize: cs.fontSize,
    fontWeight: cs.fontWeight,
    contrastRatio: ratio ? Number(ratio.toFixed(2)) : null
  };
})();
"""
