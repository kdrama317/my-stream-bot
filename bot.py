
import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

API_ID = 33592092
API_HASH = "1f7d4399f5bee82908b43aa4cb2a9f2c"
BOT_TOKEN = "8982300675:AAFVPvdfBKiYEPt1dVfTqQr7alRJy2VboPA"
PORT = int(os.environ.get("PORT", 8080))

bot = Client("file_stream_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
routes = web.RouteTableDef()

@bot.on_message(filters.command("start"))
async def start_cmd(client, message: Message):
    await message.reply_text("👋 **Bhai aapka 24x7 Live Stream Bot taiyar hai!**\n\nVideo bhejo, button waala link milega.")

@bot.on_message(filters.all & ~filters.command("start"))
async def generate_link(client, message: Message):
    media = message.document or message.video or message.audio or message.animation
    if not media:
        return
        
    file_id = media.file_id
    file_name = getattr(media, "file_name", "video.mp4") or "video.mp4"
    app_url = os.environ.get("APP_URL", f"http://localhost:{PORT}")
    
    download_link = f"{app_url}/download/{file_id}/{file_name}"
    stream_link = f"{app_url}/stream/{file_id}/{file_name}"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Download", url=download_link),
         InlineKeyboardButton("📺 Stream", url=stream_link)]
    ])
    
    await message.reply_text(
        f"✅ **Aapki File taiyar hai!**\n\n📁 **Name:** `{file_name}`",
        reply_markup=keyboard
    )

@routes.get("/download/{file_id}/{file_name}")
async def download_page_handler(request):
    file_id = request.match_info['file_id']
    file_name = request.match_info['file_name']
    html_content = f"<html><body style='font-family:Arial; background:#f4f6f9; padding:50px; text-align:center;'><div style='background:white; padding:30px; border-radius:10px; max-width:400px; margin:auto; box-shadow:0 4px 10px rgba(0,0,0,0.1);'><h3>📁 File: {file_name}</h3><br><a href='/stream/{file_id}/{file_name}' style='display:inline-block; padding:12px 25px; background:#007bff; color:white; text-decoration:none; border-radius:5px; font-weight:bold;'>Download Now</a></div></body></html>"
    return web.Response(text=html_content, content_type="text/html")

@routes.get("/stream/{file_id}/{file_name}")
async def stream_handler(request):
    file_id = request.match_info['file_id']
    file_name = request.match_info['file_name']
    async def file_sender():
        async for chunk in bot.stream_media(file_id):
            yield chunk
    return web.Response(body=file_sender(), headers={"Content-Disposition": f'attachment; filename="{file_name}"', "Content-Type": "application/octet-stream"})

async def main():
    await bot.start()
    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
    print("⚡ Bot is running live 24/7...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
