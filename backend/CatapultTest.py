import subprocess
import asyncio
import os
from pyppeteer import connect

# Waits up to 10 minutes for a tab matching a keyword
async def wait_for_tab(browser, keyword, timeout=600, interval=2):
    elapsed = 0
    while elapsed < timeout:
        pages = await browser.pages()
        for page in pages:
            if keyword.lower() in page.url.lower():
                return page
        await asyncio.sleep(interval)
        elapsed += interval
        print(f"⏳ Still waiting... {elapsed}/{timeout} seconds")
    return None

async def main():
    print("📤 Launching Chrome via subprocess...")
    subprocess.Popen([
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '--remote-debugging-port=9222',
        '--user-data-dir=/tmp/chrome-debug',
        '--no-first-run',
        '--no-default-browser-check',
        '--new-window',
        '--start-maximized',
        '--disable-backgrounding-occluded-windows',
        'https://purdue.brightspace.com/d2l/login'
    ])

    await asyncio.sleep(5)

    print("🔌 Connecting to Chrome...")
    browser = await connect(browserURL='http://localhost:9222')

    # Immediately force the Chrome window to reset its size and position via AppleScript.
    # Adjust the numbers as needed for your display.
    # This command sets the front window's bounds to: left=0, top=22, right=1440, bottom=900.
    os.system('osascript -e \'tell application "Google Chrome" to set bounds of front window to {0, 22, 1440, 900}\'')
    await asyncio.sleep(2)  # Allow time for the window to update

    print("⏳ Waiting for Brightspace tab to appear...")
    target_page = await wait_for_tab(browser, "brightspace.com/d2l/home")

    if target_page:
        print("✅ Brightspace tab found!")
        await asyncio.sleep(2)
        # Trigger a CDP repaint command (optional)
        await target_page._client.send("Emulation.clearDeviceMetricsOverride")
        # Test interaction
        await target_page.evaluate('''() => {
            alert("Automation script connected!");
        }''')
    else:
        print("❌ Could not find Brightspace tab within 10 minutes.")

    await browser.disconnect()

asyncio.get_event_loop().run_until_complete(main())
