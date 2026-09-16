import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Logging configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Configuration from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY").strip()

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Sveiki!\n\n"
        "Atsiųskite gaminio parametrus bet kokia forma (pvz., išmatavimai, odos rūšis, "
        "spalva, kišenėlių skaičius, siūlas, paskirtis ir t.t.).\n\n"
        "Aš iš karto paruošiu Vinted platformai pritaikytą aprašymą lietuvių kalba."
    )
    await update.message.reply_text(welcome_text)


async def generate_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text

    # Show typing status while the model generates text
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING
    )

    prompt = f"""
    Tu esi patyręs odos meistro asistentas ir pardavimų tekstų kūrėjas.
    Pagal pateiktus odos gaminio parametrus sugeneruok profesionalų, aiškų ir parduodantį skelbimo aprašymą Vinted platformai lietuvių kalba.

    Vartotojo pateikti parametrai:
    {user_input}

    Reikalavimai aprašymui:
    1. Pavadinimas: aiškus, patrauklus ir optimizuotas paieškai (pvz., „Rankų darbo natūralios odos kortelių dėklas“).
    2. Būklė: nurodyk „Nauja (autorinis rankų darbas)“.
    3. Specifikacija (išskirta punktais):
       - Oda ir jos savybės
       - Išmatavimai
       - Talpa / skyriai
       - Siuvimo būdas (jei paminėta – balno dygsnis, vaškuotas siūlas)
       - Kraštų apdirbimas / furnitūra (jei paminėta)
       - Visi kiti vartotojo paminėti parametrai
    4. Gaminio privalumai: 2-3 sakiniai apie ilgaamžiškumą, tvirtumą, laikui bėgant atsirandančią unikalią patiną ir tinkamumą dovanai.
    5. Žymos (Hashtags): 8-12 populiarių žymų Vinted paieškai (pvz., #oda #rankudarbas #pinigine ir pan.).

    SVARBU:
    - Nenaudok jokių įžanginių ar baigiamųjų frazių (tokių kaip „Štai jūsų aprašymas“).
    - Pateik tik paruoštą tekstą, kurį galima iškart nukopijuoti į Vinted.
    """

    try:
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Klaida generuojant aprašymą: {e}")
        await update.message.reply_text(
            "Atsiprašome, įvyko klaida generuojant tekstą. Bandykite dar kartą."
        )


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, generate_description)
    )

    logging.info("Botas paleistas ir laukia pranešimų...")
    app.run_polling()


if __name__ == "__main__":
    main()