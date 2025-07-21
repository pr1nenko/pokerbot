from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import random
import asyncio
import nest_asyncio
import re
from itertools import combinations
nest_asyncio.apply()
TOKEN = "8185411618:AAEdPhiBivpXkvqDDcNbJShJLgHdX43JFFg"
SUITS = ['♠️', '♥️', '♦️', '♣️']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
}
deck = [rank + suit for suit in SUITS for rank in RANKS]
keyboard = [
    ['/start', '/rules'],
    ['/deal', '/flop'],
    ['/turn', '/river'],
    ['/show', '/combo'],
    ['/strategy', '/faq']
]
reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
player_hand = []
community_cards = {
    'flop': [],
    'turn': None,
    'river': None
}
current_stage = "none"
def extract_rank(card):
    match = re.match(r"([2-9]|10|[JQKA])[♠♥♦♣♠️♥️♦️♣️]", card)
    return match.group(1) if match else None
def evaluate_hand(cards):
    ranks = []
    for card in cards:
        rank = extract_rank(card)
        if rank and rank in RANK_VALUES:
            ranks.append(RANK_VALUES[rank])
    if len(ranks) < 5:
        return "старша карта"
    numeric_ranks = sorted(ranks, reverse=True)
    unique_ranks = sorted(set(numeric_ranks), reverse=True)
    rank_counts = {r: numeric_ranks.count(r) for r in unique_ranks}
    count_rank = {}
    for r, c in rank_counts.items():
        count_rank.setdefault(c, []).append(r)
    suits = [card[-1] for card in cards if card[-1] in SUITS]
    is_flush = len(set(suits)) == 1
    is_straight = len(unique_ranks) == 5 and max(unique_ranks) - min(unique_ranks) == 4
    if sorted(unique_ranks) == [10, 11, 12, 13, 14] and is_flush:
        return "флеш-рояль"
    elif is_straight and is_flush:
        return "стріт-флеш"
    elif 4 in count_rank:
        return "каре"
    elif 3 in count_rank and 2 in count_rank:
        return "фул-хаус"
    elif is_flush:
        return "флеш"
    elif is_straight:
        return "стріт"
    elif 3 in count_rank:
        return "трійка"
    elif len(count_rank.get(2, [])) >= 2:
        return "дві пари"
    elif 2 in count_rank:
        return "пара"
    else:
        return "старша карта"
async def deal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global player_hand, community_cards, current_stage
    random.shuffle(deck)
    player_hand = deck[:2]
    community_cards = {
        'flop': deck[2:5],
        'turn': deck[5],
        'river': deck[6]
    }
    current_stage = "preflop"
    await update.message.reply_text(f"🎴 Твоя рука: {', '.join(player_hand)}")
    await update.message.reply_text("Пишіть /flop, щоб відкрити 3 карти на столі.")
async def flop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_stage
    if current_stage != "preflop":
        await update.message.reply_text("⚠️ Спочатку роздайте карти (/deal)")
        return
    current_stage = "flop"
    cards = community_cards['flop']
    await update.message.reply_text(f"🃏 Карти на столі (flop): {', '.join(cards)}")
    await update.message.reply_text("Пишіть /turn, щоб відкрити ще одну карту.")
async def turn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_stage
    if current_stage != "flop":
        await update.message.reply_text("⚠️ Спочатку відкрийте flop.")
        return
    current_stage = "turn"
    card = community_cards['turn']
    await update.message.reply_text(f"🃏 Карта turn: {card}")
    await update.message.reply_text("Пишіть /river, щоб відкрити останню карту.")
async def river(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_stage
    if current_stage != "turn":
        await update.message.reply_text("⚠️ Спочатку відкрийте turn.")
        return
    current_stage = "river"
    card = community_cards['river']
    await update.message.reply_text(f"🃏 Карта river: {card}")
    await update.message.reply_text("🏁 Ось усі карти. Напишіть /show, щоб визначити комбінацію.")
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global player_hand, community_cards, current_stage
    if current_stage == "none":
        await update.message.reply_text("⚠️ Спочатку роздайте карти (/deal)")
        return
    combined = player_hand + community_cards['flop']
    if current_stage in ["turn", "river"]:
        combined.append(community_cards['turn'])
    if current_stage == "river":
        combined.append(community_cards['river'])
    best_combo = "старша карта"
    best_score = -1
    for combo in combinations(combined, 5):
        combo_list = list(combo)
        combo_name = evaluate_hand(combo_list)
        score = get_combo_score(combo_name)
        if score > best_score:
            best_score = score
            best_combo = combo_name
    await update.message.reply_text(f"🃏 Твоя рука + столі: {', '.join(player_hand + community_cards['flop'])}")
    if current_stage in ["turn", "river"]:
        await update.message.reply_text(f" + {community_cards['turn']}")
    if current_stage == "river":
        await update.message.reply_text(f" + {community_cards['river']}")
    await update.message.reply_text(f"🏆 Твоя комбінація: {best_combo.capitalize()}")
def get_combo_score(combo):
    scores = {
        "флеш-рояль": 10,
        "стріт-флеш": 9,
        "каре": 8,
        "фул-хаус": 7,
        "флеш": 6,
        "стріт": 5,
        "трійка": 4,
        "дві пари": 3,
        "пара": 2,
        "старша карта": 1
    }
    return scores.get(combo, 0)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global reply_markup
    await update.message.reply_text(
        "👋 Привіт! Я покер-бот. Я допоможу тобі навчитися грати в покер!\n\n"
        "Обери команду нижче або напиши вручну.",
        reply_markup=reply_markup
    )
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
async def tip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poker_tips = [
        "Не грай кожну руку — обирай лише сильні.",
        "Пам'ятай: позиція за столом має значення.",
        "Будь уважним до ставок суперників.",
        "Не виплачувай без сильної руки."
    ]
    tip = random.choice(poker_tips)
    await update.message.reply_text(f"💡 Порада: {tip}")
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    exception = context.error
    if isinstance(exception, Conflict):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🛑 Бот вже запущений. Переконайся, що запущено лише один екземпляр."
        )
    elif isinstance(exception, KeyError):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Невідома карта. Спробуйте ще раз."
        )
    else:
        print(f"❌ Невідома помилка: {exception}")
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("deal", deal))
    app.add_handler(CommandHandler("flop", flop))
    app.add_handler(CommandHandler("turn", turn))
    app.add_handler(CommandHandler("river", river))
    app.add_handler(CommandHandler("show", show))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("combo", combo))
    app.add_handler(CommandHandler("strategy", strategy))
    app.add_handler(CommandHandler("faq", faq))
    app.add_handler(CommandHandler("tip", tip))
    app.add_error_handler(error_handler)
    await app.run_polling()
def test_evaluate_hand():
    test_cases = [
        (["10♠️", "J♠️", "Q♠️", "K♠️", "A♠️"], "флеш-рояль"),
        (["8♥️", "9♥️", "10♥️", "J♥️", "Q♥️"], "стріт-флеш"),
        (["K♠️", "K♥️", "K♦️", "K♣️", "2♠️"], "каре"),
        (["A♠️", "A♥️", "A♦️", "Q♣️", "Q♠️"], "фул-хаус"),
        (["2♠️", "5♠️", "7♠️", "J♠️", "K♠️"], "флеш"),
        (["6♠️", "7♥️", "8♦️", "9♣️", "10♠️"], "стріт"),
        (["Q♠️", "Q♥️", "Q♦️", "7♣️", "2♠️"], "трійка"),
        (["J♠️", "J♥️", "5♦️", "5♠️", "A♣️"], "дві пари"),
        (["10♠️", "10♥️", "3♦️", "6♣️", "K♠️"], "пара"),
        (["A♠️", "K♥️", "Q♦️", "9♣️", "2♠️"], "старша карта"),
    ]

    print("🧪 Тестування комбінацій:")
    for cards, expected in test_cases:
        result = evaluate_hand(cards)
        print(f"{' '.join(cards)} → {result} — {'✅ OK' if result == expected else '❌ Помилка'}")
if __name__ == '__main__':
    test_evaluate_hand()
    asyncio.run(main())