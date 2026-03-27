import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from config import SERVICES, TELEGRAM_BOT_TOKEN, AUTHOR_INFO, DONATE_INFO
from providers import PROVIDER_REGISTRY, JSONProvider
from models import ProviderConfig

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class PriceBot:
    def __init__(self, token: str, services: list[ProviderConfig]):
        self.token = token
        self.services = services
        self.providers = {
            s.command: PROVIDER_REGISTRY.get(s.provider_type, JSONProvider)(s)
            for s in services
        }

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Hiển thị menu chính với các nút bấm động"""
        keyboard = [
            [InlineKeyboardButton(f"🔍 {s.name}", callback_data=f"query_{s.command}")]
            for s in self.services
        ]
        keyboard.append([InlineKeyboardButton("ℹ️ Tác giả & Donate", callback_data="info")])

        await update.message.reply_text(
            "👋 Chào mừng bạn đến với Bot Tra Cứu Giá!\n"
            "Chọn một dịch vụ bên dưới để xem thông tin mới nhất:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Hiển thị thông tin tác giả và donate"""
        message_text = f"{AUTHOR_INFO}\n\n{DONATE_INFO}"

        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.message.reply_text(message_text, parse_mode="Markdown")
        else:
            await update.message.reply_text(message_text, parse_mode="Markdown")

    async def handle_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý khi người dùng nhấn nút hoặc gõ lệnh"""
        query = update.callback_query

        if query:
            await query.answer()
            command = query.data.replace("query_", "")
            message = query.message
        else:
            command = update.message.text.replace("/", "").split("@")[0]
            message = update.message

        provider = self.providers.get(command)
        if provider:
            status_msg = await message.reply_text(f"⏳ Đang lấy dữ liệu {provider.config.name}...")
            result = await provider.fetch_data()
            await status_msg.edit_text(result, parse_mode="Markdown")
        else:
            await message.reply_text("❌ Dịch vụ không tồn tại.")

    async def _post_init(self, app: Application):
        """Thiết lập danh sách lệnh sau khi app khởi tạo xong."""
        commands_list = [BotCommand("start", "Menu chính")]
        for s in self.services:
            commands_list.append(BotCommand(s.command, f"Xem {s.name}"))
        commands_list.append(BotCommand("info", "Thông tin tác giả & Donate"))
        await app.bot.set_my_commands(commands_list)

    def run(self):
        """Khởi chạy Bot"""
        if not self.token:
            print("⚠️ LỖI: Bạn chưa điền TELEGRAM_BOT_TOKEN trong config.py")
            return

        app = Application.builder().token(self.token).post_init(self._post_init).build()

        app.add_handler(CommandHandler("start", self.start))
        for cmd in self.providers:
            app.add_handler(CommandHandler(cmd, self.handle_query))
        app.add_handler(CommandHandler("info", self.info))

        app.add_handler(CallbackQueryHandler(self.handle_query, pattern=r"^query_"))
        app.add_handler(CallbackQueryHandler(self.info, pattern=r"^info$"))

        print(f"✅ Bot đã sẵn sàng với {len(self.services)} dịch vụ.")
        app.run_polling()


if __name__ == "__main__":
    bot = PriceBot(TELEGRAM_BOT_TOKEN, SERVICES)
    bot.run()
