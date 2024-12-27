from telegram.ext import Application, CommandHandler,ContextTypes
from telegram import Update
from pymongo import MongoClient
from bson.json_util import dumps
cliente = MongoClient('mongodb+srv://avazquez2:12341234_A@test.xxra8.mongodb.net/?retryWrites=true&w=majority&appName=Test')
client_db = cliente.SUPERMERCATS
productes = client_db.productes
carrito = {}

for p in productes.find():
    carrito[int(p['id'])] = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inform user about what this bot can do"""
    await update.message.reply_text(
        "Benvingut a la nostra tenda \n"
        "Si necesitas alguna comanda i no saps com es fa utilitza la comanda - /help"
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inform user about what this bot can do"""
    await update.message.reply_text(
        "Les comendes disponibles son \n"
        "/start - Inicia el bot\n"
        "/help - Mostra aquest missatge\n"
        "/mostrarTenda - Mostra tots els productes disponibles\n"
        "/producte - Mostra l'informacio important d'un producte\n"
        "/imatge - Mostra la imatge d'un producte\n"
        "/afegirproducte - Afegeix un producte al carrito\n"
        "/mostrarCarrito - Mostra el carrito\n"
        "/acabarCompra - Acaba la compra i reinicia el carrito\n"
    )

async def producte(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
            product_id = str(context.args[0])
            producte = productes.find_one({"id": product_id})
            if producte:
                await update.message.reply_text(
                    f"Mostrant l'informacio del producte amb ID: {producte['id']} \n"
                    f"Nom: {producte['nom']}\n"
                    f"Preu: {producte['preu']}\n")
            else:
                await update.message.reply_text("Aquest no es un ID de producte valid.")
    else:
        await update.message.reply_text("Recorda en posar un ID de producte.")

async def imatge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
            product_id = str(context.args[0])
            producte = productes.find_one({"id": product_id})
            if producte:
                await update.message.reply_photo(
                    photo=producte['imatge']
                )
            else:
                await update.message.reply_text("Aquest no es un ID de producte valid.")
    else:
        await update.message.reply_text("Recorda en posar un ID de producte.")


async def afegirproducte(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
            product_id = str(context.args[0])
            id = int(context.args[0])
            num_productes = int(context.args[1])
            producte = productes.find_one({"id": product_id})
            if producte:
                carrito[id] += num_productes
                preuTotal = float(producte['preu']) * num_productes
                await update.message.reply_text(
                    f"Producte afegit al carrito\n"
                    f"Nom: {producte['nom']}\n"
                    f"Quantitat: {num_productes}\n"
                    f"preuTotal: {preuTotal:.2f}\n")
            else:
                await update.message.reply_text("Aquest no es un ID de producte valid.")
    else:
        await update.message.reply_text("Recorda en posar un ID de producte.")


async def mostrarCarrito(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response = "El teu carrito:\n"
    preuTotal = 0 
    for prod in carrito:
        if carrito[prod] > 0:
            producte = productes.find_one({"id": str(prod)})
            if producte:
                preuProducte = float(producte['preu']) * carrito[prod]
                response += (
                    f"Producte: {producte['nom']} \n"
                    f"Quantitat: {carrito[prod]} \n"
                    f"Preu: {preuProducte:.2f}\n\n"
                )
                preuTotal += preuProducte
            else:
                response += f"Producte amb ID {prod} no trobat a la base de dades.\n\n"
    if response == "El teu carrito:\n":
        response = "No hi ha res al teu carrito."
    else:
        response += f"Preu total: {preuTotal:.2f}"

    await update.message.reply_text(response)

async def acabarCompra(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global carrito
    carrito.clear() 
    await update.message.reply_text("Compra finalitzada. Pasi per caixa per pagar.")

async def mostrarTenda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    for p in productes.find():
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=p['imatge'],
            caption=(
                f"ID: {p['id']} \n"
                f"Nom: {p['nom']}\n"
                f"Preu: {p['preu']}\n"
            )
        )
    await update.message.reply_text("Per comprar un producte utilitza la comanda \n /afegirproducte IDProducte Quantitat")


def main():
    # declara una constant amb el access token que llegeix de token.txt
    TOKEN = open('./token.txt').read().strip()
    print(TOKEN)
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('producte', producte))
    application.add_handler(CommandHandler('imatge', imatge))
    application.add_handler(CommandHandler('afegirproducte', afegirproducte))
    application.add_handler(CommandHandler('mostrarCarrito', mostrarCarrito))
    application.add_handler(CommandHandler('acabarCompra', acabarCompra))
    application.add_handler(CommandHandler('mostrarTenda', mostrarTenda))
    application.run_polling()


if __name__ == '__main__':
    main()