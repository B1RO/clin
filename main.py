from playwright.async_api import async_playwright
import fire
import sys
import asyncio
import shutil
import subprocess
import psutil

async def wait_message_streaming_visible(locator):
    return await locator.locator(".result-streaming").wait_for(state="visible")


def run_server_if_not_running(headless=False):
    server_script = "server.py"
    run_command = ["python", server_script, "--daemon"]

    if headless:
        run_command.append('--headless')

    # Check if the server is already running
    for process in psutil.process_iter(attrs=['pid', 'cmdline']):
        cmdline = process.info['cmdline']
        if cmdline and server_script in ' '.join(cmdline):
            print(f"{server_script} is already running with PID {process.info['pid']}")
            return

    # If not running, start the server
    print(f"Starting {server_script} with  headless mode: {headless}...")
    subprocess.Popen(run_command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    print(f"{server_script} has been started.")






async def login_async(username, password):
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        default_context = browser.contexts[0]
        page = default_context.pages[0]
        await page.goto("http://chat.openai.com")
        await page.get_by_role("button", name="Log in").click()
        await page.get_by_role("textbox").fill(username)
        await page.get_by_role("button", name="Continue", exact=True).click()
        await page.get_by_role("textbox").fill(password)
        await page.get_by_role("button", name="Continue", exact=True).click()
        await page.get_by_role('button', name='Next').click();
        await page.get_by_role('button', name='Next').click();
        await page.get_by_role('button', name='Done').click();
        await page.get_by_role('button', name='Dismiss').click();


async def new_chat_async():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        default_context = browser.contexts[0]
        page = default_context.pages[0]
        all_div_elements = await page.locator('a').filter(has_text="New chat").first.click()


async def open_assitant(headless):
    run_server_if_not_running(headless)
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        default_context = browser.contexts[0]
        page = default_context.pages[0]
        await page.goto("http://chat.openai.com")

async def open_assistant_headless():
    return await open_assitant(True)
async def open_assistant_no_headless():
    return await open_assitant(False)


async def switch_to_4():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        default_context = browser.contexts[0]
        page = default_context.pages[0]
        await page.get_by_text("GPT-4").click()


async def switch_to_3():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        default_context = browser.contexts[0]
        page = default_context.pages[0]
        await page.get_by_text("GPT-3.5").click()



async def stream_message(page):
    last_text = ""
    terminal_width, _ = shutil.get_terminal_size()

    while True:
        current_text = await page.locator("main .group").filter(has_not_text="?").last.inner_text()

        if current_text != last_text:
            print(current_text[len(last_text):], end="")
            last_text = current_text

        if await page.locator(".result-streaming").count() == 0:
            break

        await asyncio.sleep(0.100)
    print("\n")




async def get_nth_message(n):
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        default_context = browser.contexts[0]
        page = default_context.pages[0]
        print(await page.locator("main .group").filter(has_not_text="?").nth(n).inner_text())


async def send_message_async(message):
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        default_context = browser.contexts[0]
        page = default_context.pages[0]
        await page.get_by_role("textbox").fill(message)
        await page.locator("form").get_by_role("button").last.click()
        await wait_message_streaming_visible(page.locator("main .group"))
        await stream_message(page)


def new_chat():
    asyncio.run(new_chat_async())


def send_message(message=None):
    if message is None:
        # Read the message from stdin
        message = sys.stdin.read().strip()
    asyncio.run(send_message_async(message))


def close():
    server_script = "server.py"
    command = ["python", server_script, "--kill"]

    print(f"Running {server_script} with --kill flag...")
    result = subprocess.run(command)

    if result.returncode == 0:
        print(f"{server_script} terminated successfully.")
    else:
        print(f"An error occurred while terminating {server_script}.")


def login(username, password):
    asyncio.run(login_async(username, password))


if __name__ == '__main__':
    fire.Fire({
        'm': send_message,
        'l': login,
        'o': open_assistant_no_headless,
        'oh': open_assistant_headless,
        "c" : close,
        'n': new_chat,
        "3": switch_to_3,
        "4": switch_to_4,
        "g" : get_nth_message
    })
