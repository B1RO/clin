import asyncio
import time
from playwright.async_api import async_playwright
import fire
import sys

async def is_result_streaming_class_present(locator):
        return await locator.locator(".result-streaming").wait_for(state="detached"),


async def login_async(username,password):
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
        await page.get_by_role('button',  name='Next').click();
        await page.get_by_role('button',  name='Next').click();
        await page.get_by_role('button', name='Done').click();
       	await page.get_by_role('button', name='Dismiss').click();

async def send_message_async(message):
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        default_context = browser.contexts[0]
        page = default_context.pages[0]                
        await page.get_by_role("textbox").fill(message)
        await page.locator("form").get_by_role("button").last.click()
        await is_result_streaming_class_present(page.locator("main .group"))
        i = await page.locator("main .group").count()
        print(await page.locator("main .group").nth(i-2).inner_text())

def default_command(ctx, param, value):
    if value and not ctx.resilient_parsing:
        asyncio.run(send_message_async(value))

def send_message(message):
	asyncio.run(send_message_async(message))

def login(username,password):
        asyncio.run(login_async(username,password))


if __name__ == '__main__':
        fire.Fire({
            'm': send_message,
            'l': login,
        })
