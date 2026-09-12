
fromttelegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters, CallbackContext

# تنظیمات لاگ‌گیری
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8670608043:AAGfoDa5s6-nhIXrINGxPjRq4xnEXGcUXZ8"
OWNER_ID = 7173076966

ADMINS_FILE = "admins.txt"
user_states = {}

def load_admins():
    admins = {OWNER_ID}
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line.isdigit():
                    admins.add(int(line))
    return admins

def save_admin(admin_id):
    admins = load_admins()
    if admin_id not in admins:
        with open(ADMINS_FILE, "a") as f:
            f.write(f"{admin_id}\n")

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_states[user_id] = "WAITING_FOR_ID"
    update.message.reply_text("سلام! لطفاً شناسه (یا کدی) که در پنل ثبت کرده‌اید را ارسال کنید:")

def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    text = update.message.text
    user_name = update.effective_user.first_name or "کاربر ناشناس"
    
    if user_states.get(user_id) == "WAITING_FOR_ID":
        entered_id = text.strip()
        user_states[user_id] = "REGISTERED"
        
        update.message.reply_text(f"✅ شناسه شما ({entered_id}) با موفقیت ثبت شد و برای بررسی به مدیریت ارسال گردید.")
        
        keyboard = [
            [
                InlineKeyboardButton("✅ تأیید", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton("❌ رد کردن", callback_data=f"cancel_{user_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        admin_message = (
            f"📥 **درخواست ثبت‌نام شناسه جدید:**\n\n"
            f"👤 نام کاربر: {user_name}\n"
            f"🆔 آیدی تلگرام: `{user_id}`\n"
            f"📌 شناسه وارد شده: {entered_id}"
        )
        
        current_admins = load_admins()
        for admin_id in current_admins:
            try:
                context.bot.send_message(
                    chat_id=admin_id,
                    text=admin_message,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
            except Exception as e:
                logging.error(f"خطا در ارسال پیام به ادمین {admin_id}: {e}")
    else:
        update.message.reply_text("شما قبلاً ثبت‌نام کرده‌اید یا دستوری نفرستادید. برای شروع /start را بزنید.")

def add_admin(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        update.message.reply_text("⛔️ متأسفم، این دستور فقط توسط مالک ربات قابل استفاده است.")
        return
    
    if not context.args:
        update.message.reply_text("⚠️ لطفاً آیدی عددی کاربر را وارد کنید.\nمثال:\n`/add_admin 123456789`", parse_mode="Markdown")
        return
    
    try:
        new_admin_id = int(context.args[0])
        save_admin(new_admin_id)
        update.message.reply_text(f"✅ کاربر با آیدی `{new_admin_id}` با موفقیت به لیست ادمین‌ها اضافه شد.", parse_mode="Markdown")
        context.bot.send_message(chat_id=new_admin_id, text="🎉 تبریک! شما به عنوان ادمین جدید ربات منصوب شدید.")
    except ValueError:
        update.message.reply_text("❌ آیدی نامعتبر است. لطفاً فقط عدد وارد کنید.")

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    admin_id = query.from_user.id
    
    current_admins = load_admins()
    if admin_id not in current_admins:
        query.answer("⛔️ شما اجازه انجام این کار را ندارید!", show_alert=True)
        return
    
    query.answer()
    data = query.data
    action, target_user_id = data.split("_")
    target_user_id = int(target_user_id)
    admin_name = query.from_user.first_name
    
    if action == "approve":
        query.edit_message_text(text=f"{query.message.text}\n\n✅ **وضعیت:** تأیید و ارسال شد.\n👤 تأیید شده توسط: {admin_name}")
        context.bot.send_message(chat_id=target_user_id, text="🎉 اطلاعات و درخواست شما توسط مدیریت تأیید شد!")
    elif action == "cancel":
        query.edit_message_text(text=f"{query.message.text}\n\n❌ **وضعیت:** لغو شد.\n👤 لغو شده توسط: {admin_name}")
        context.bot.send_message(chat_id=target_user_id, text="⚠️ درخواست شما توسط مدیریت رد شد. لطفاً دوباره تلاش کنید.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add_admin", add_admin))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))

    print("ربات روشن شد و در حال اجراست...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
