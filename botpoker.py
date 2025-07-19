from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
import asyncio
import nest_asyncio
nest_asyncio.apply()
SUITS = ['♠️', '♥️', '♦️', '♣️']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
deck = [rank + suit for suit in SUITS for rank in RANKS]
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привіт! Я покер-бот. Я допоможу тобі навчитися грати в покер!\n\n"
        "Ось, що я можу:\n"
        "/start — початок роботи\n"
        "/rules — правила покеру\n"
        "/combo — пояснення комбінацій\n"
        "/strategy — стратегія початківця\n"
        "/faq — поширені запитання\n"
        "/cards — випадкові 5 карт для тренування"
    )
async def cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    random.shuffle(deck)
    hand = deck[:5]
    await update.message.reply_text("🃏 Ось твої карти: " + ', '.join(hand))
async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rules_text = (
        "🎯 Основні правила покеру (техаський холдем):\n"
        "1. У кожного гравця по 2 закриті карти.\n"
        "2. На столі 5 спільних карт (flop, turn, river).\n"
        "3. Мета — скласти найкращу 5-картну комбінацію.\n"
        "4. Гравці можуть: чекати, пасувати, викликати, підвищувати.\n"
        "5. Переможець — той, у кого краща комбінація або хто залишився один."
    )
    await update.message.reply_text(rules_text)
async def combo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    combo_text = (
        "🏆 Комбінації в покері (від найкращої до найгіршої):\n"
        "1. Флеш-рояль — 10, В, Д, К, А однієї масті\n"
        "2. Стріт-флеш — 5 послідовних карт однієї масті\n"
        "3. Каре — 4 однакові карти\n"
        "4. Фул-хаус — трійка + пара\n"
        "5. Флеш — 5 карт однієї масті\n"
        "6. Стріт — 5 послідовних карт\n"
        "7. Трійка — 3 однакові карти\n"
        "8. Дві пари\n"
        "9. Одна пара\n"
        "10. Старша карта"
    )
    await update.message.reply_text(combo_text)
async def strategy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    strategy_text = (
        "🧠 Базова стратегія для початківців:\n"
        "1. Грай лише сильні початкові руки: AA, KK, QQ, AK, JJ, AQ.\n"
        "2. Спостерігай за іншими гравцями.\n"
        "3. Не виплачувай великі суми без сильної руки.\n"
        "4. Вивчи позиції за столом (чемпіон, батон, блайнди).\n"
        "5. Не грай відразу на великі суми — практикуйся на мікролімітах."
    )
    await update.message.reply_text(strategy_text)
async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    faq_text = (
        "❓ Часті запитання:\n\n"
        "Q: Як визначається переможець?\n"
        "A: Переможець — той, у кого краща 5-картна комбінація або хто залишився один.\n\n"
        "Q: Що таке блайнди?\n"
        "A: Обов'язкові ставки, які роблять гравці до початку кожної руки.\n\n"
        "Q: Як виграти у новачка?\n"
        "A: Не грай кожну руку, стеж за ставками, не втрачай контроль над банком."
    )
    await update.message.reply_text(faq_text)
async def main():
    app = ApplicationBuilder().token("8185411618:AAEdPhiBivpXkvqDDcNbJShJLgHdX43JFFg").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cards", cards))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("combo", combo))
    app.add_handler(CommandHandler("strategy", strategy))
    app.add_handler(CommandHandler("faq", faq))
    await app.run_polling()
if __name__ == '__main__':
    asyncio.run(main())