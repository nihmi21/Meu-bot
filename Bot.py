import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 🔐 VARIÁVEIS DO RAILWAY
TOKEN = os.getenv("TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not TOKEN:
    raise ValueError("TOKEN não encontrado no ENV")

if not ADMIN_ID:
    raise ValueError("ADMIN_ID não encontrado no ENV")

ADMIN_ID = int(ADMIN_ID)

# 📱 MENU
menu = [
    ["🔍 Consultar veículo"],
    ["🚨 Problema no carro"],
    ["💰 Orçamento"],
    ["📅 Agendar"],
    ["📲 WhatsApp"]
]

# 🔍 CONSULTA DE PLACA (PRECISA API REAL)
def consultar_placa(placa):
    url = f"https://api.exemplo.com/veiculo/{placa}"
    headers = {"Authorization": "Bearer SUA_API_KEY_AQUI"}

    try:
        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code == 200:
            d = r.json()
            return (
                f"🚗 *Resultado da consulta:*\n\n"
                f"Marca: {d.get('marca')}\n"
                f"Modelo: {d.get('modelo')}\n"
                f"Ano: {d.get('ano')}\n"
                f"Situação: {d.get('situacao')}"
            )
        else:
            return "❌ Não consegui consultar. Verifique a placa."
    except:
        return "⚠️ Erro na consulta."

# ▶️ START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚗 *LealCar Oficina Móvel*\n\nAtendimento rápido na sua casa 🔧\n\nEscolha uma opção:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(menu, resize_keyboard=True)
    )

# 🧠 LÓGICA PRINCIPAL
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    msg = update.message.text.lower()

    # 🔍 CONSULTA
    if "consultar" in msg:
        await update.message.reply_text("Digite a placa (ex: ABC1234):")
        context.user_data["etapa"] = "placa"

    elif context.user_data.get("etapa") == "placa":
        placa = msg.upper()

        resultado = consultar_placa(placa)
        await update.message.reply_text(resultado, parse_mode="Markdown")

        # 🔔 AVISO PRA VOCÊ
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔍 Consulta realizada\nPlaca: {placa}\nCliente: {user.first_name}"
        )

        # 💰 GANCHO DE VENDA
        await update.message.reply_text(
            "🔧 Quer que eu avalie esse carro ou faça manutenção?\n\nFale comigo 👇\nhttps://wa.me/5551993880577"
        )

        context.user_data.clear()

    # 🚨 PROBLEMA
    elif "problema" in msg:
        await update.message.reply_text(
            "O que aconteceu?\n1 - Não liga\n2 - Barulho\n3 - Outro"
        )
        context.user_data["etapa"] = "problema"

    elif context.user_data.get("etapa") == "problema":
        context.user_data["problema"] = msg
        await update.message.reply_text("Qual seu nome?")
        context.user_data["etapa"] = "nome"

    elif context.user_data.get("etapa") == "nome":
        context.user_data["nome"] = msg
        await update.message.reply_text("Seu WhatsApp?")
        context.user_data["etapa"] = "telefone"

    elif context.user_data.get("etapa") == "telefone":
        nome = context.user_data.get("nome")
        problema = context.user_data.get("problema")
        telefone = msg

        # 🔔 AVISO PRA VOCÊ
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔥 Novo cliente!\nNome: {nome}\nTelefone: {telefone}\nProblema: {problema}"
        )

        await update.message.reply_text(
            "✅ Recebido!\n\nVou te chamar no WhatsApp 👇\nhttps://wa.me/5551993880577"
        )

        context.user_data.clear()

    # 💰 ORÇAMENTO
    elif "orçamento" in msg:
        await update.message.reply_text("Me diga o carro e o problema:")
        context.user_data["etapa"] = "orcamento"

    elif context.user_data.get("etapa") == "orcamento":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💰 Pedido de orçamento:\n{msg}"
        )

        await update.message.reply_text(
            "👍 Recebi!\n\nTe chamo no WhatsApp 👇\nhttps://wa.me/5551993880577"
        )

        context.user_data.clear()

    # 📅 AGENDAR
    elif "agendar" in msg:
        await update.message.reply_text("Qual horário? Manhã / Tarde / Noite")
        context.user_data["etapa"] = "agendar"

    elif context.user_data.get("etapa") == "agendar":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📅 Cliente quer agendar: {msg}"
        )

        await update.message.reply_text(
            "✅ Pré-agendado!\n\nFinalize aqui 👇\nhttps://wa.me/5551993880577"
        )

        context.user_data.clear()

    # 📲 WHATSAPP
    elif "whatsapp" in msg:
        await update.message.reply_text(
            "📲 Fale comigo:\nhttps://wa.me/5551993880577"
        )

    else:
        await update.message.reply_text("Escolhe uma opção no menu 👍")

# 🚀 INICIAR BOT
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

print("Bot rodando 24h 🔥")
app.run_polling()
