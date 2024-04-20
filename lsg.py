from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler
import requests
import yaml

# Load bot token from bot_config.yml
with open("bot_config.yml", "r") as f:
    config = yaml.safe_load(f)
bot_token = config.get("bot_token")

# URL của API để lấy danh sách sản phẩm theo từ khóa
api_url_commission_keyword = "https://api.chietkhau.pro/api/v1/shopee/get-product-by-keyword"

# URL của API để lấy thông tin sản phẩm bằng liên kết
api_url_commission_link = "https://api.chietkhau.pro/api/v1/shopee/product-commission"

# URL của API để chuyển đổi liên kết
api_url_convert = "https://area08.000webhostapp.com/change_link/change.php"

# Hàm để gửi yêu cầu POST đến API và lấy danh sách sản phẩm theo từ khóa
async def get_product_data_by_keyword(keyword):
    payload = {"keyword": keyword}
    response = requests.post(api_url_commission_keyword, data=payload)
    response.raise_for_status()
    return response.json()

# Hàm để gửi yêu cầu POST đến API và lấy thông tin sản phẩm bằng liên kết
async def get_product_data_by_link(link):
    payload = {"link": link}
    response = requests.post(api_url_commission_link, data=payload)
    response.raise_for_status()
    return response.json()

# Hàm để chuyển đổi liên kết
async def convert_link(content):
    user_cookie = "SPC_EC=.N3U0WVo5NUtqT2cyR1Z2NCWcV89jDSfBVw+TtVSFzMQKh8vytHh6wDvC87kJnBCipw+VC9ZEslAfkmW62oauHjMOyJx/dLiyfEIlaq/XYbiMQG0fBf4/MR0/Zg3vYvASeFEjBlW79KsK96kEqyDKAUr1F+mH6K8iwJP5sHq34XjBp4EZAwo98CejjztOtDU8RH3UU5/39LkSzVjTZh2rGw=="
    data = {"content": content, "userCookie": user_cookie}
    response = requests.post(api_url_convert, data=data)
    response.raise_for_status()
    return response.text

# Hàm xử lý lệnh /shopee của người dùng (tìm kiếm bằng tên sản phẩm)
async def handle_shopee_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    # Kiểm tra xem người dùng đã cung cấp từ khóa sản phẩm chưa
    if len(args) == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Vui lòng cung cấp từ khóa sản phẩm sau lệnh /shopee.")
        return
    
    # Lấy từ khóa từ tin nhắn
    keyword = args[0]

    # Lấy danh sách sản phẩm từ API theo từ khóa
    product_data = await get_product_data_by_keyword(keyword)

    # Kiểm tra xem API trả về dữ liệu hay không
    if product_data.get("status") != "success":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Không lấy được dữ liệu sản phẩm!")
        return
    
    # Lọc 5 sản phẩm đầu tiên từ danh sách
    product_list = product_data.get("productList", [])
    top_5_products = product_list[:5]

    # Gửi thông tin về 5 sản phẩm đầu tiên và chuyển đổi liên kết
    for product in top_5_products:
        product_name = product.get("productName", "")
        shop_name = product.get("shopName", "")
        price = product.get("price", "")
        commission = product.get("commission", "")
        product_link = product.get("productLink", "")

        # Chuyển đổi liên kết sản phẩm
        converted_link = await convert_link(product_link)

        # Tạo phản hồi với thông tin sản phẩm
        response_text = (
            f"Mua hàng hoàn tiền Shopee\n"
            f"- Tên Sản Phẩm: {product_name}\n"
            f"- Tên Shop: {shop_name}\n"
            f"- Giá Tiền: {price} đ\n"
            f"- Hoa hồng bạn nhận: {commission} đ\n"
            f"👉 Link Mua Sản Phẩm: {converted_link}\n\n"
            f"---------------------\n"
            f"Powered By NhaNgheoSanSale\n"
        )

        # Gửi phản hồi đến người dùng sử dụng phương thức send_message
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

# Hàm xử lý lệnh /check của người dùng (tìm kiếm bằng liên kết sản phẩm)
async def handle_check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    # Kiểm tra xem người dùng đã cung cấp liên kết sản phẩm chưa
    if len(args) == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Vui lòng cung cấp liên kết sản phẩm sau lệnh /check.")
        return
    
    # Lấy liên kết sản phẩm từ tin nhắn
    product_link = args[0]

    # Lấy dữ liệu từ API hoa hồng bằng liên kết
    product_data = await get_product_data_by_link(product_link)

    # Chuyển đổi liên kết bằng cách gọi API chuyển đổi
    converted_link = await convert_link(product_link)

    # Tạo phản hồi với dữ liệu từ API
    response_text = "Không lấy được dữ liệu sản phẩm!"  # Giá trị mặc định nếu không có dữ liệu

    if "productInfo" in product_data:
        product_info = product_data["productInfo"]
        response_text = (
            f"Mua hàng hoàn tiền Shopee\n"
            f"- Tên Sản Phẩm: {product_info.get('productName', '')}\n"
            f"- Tên Shop: {product_info.get('shopName', '')}\n"
            f"- Giá Tiền: {product_info.get('price', '')} đ\n"
            f"- Hoa hồng bạn nhận: {product_info.get('commission', '')} đ\n"
            f"👉 Link Mua Sản Phẩm: {converted_link}\n\n"
            f"---------------------\n"
            f"Powered By NhaNgheoSanSale\n"
        )

    # Gửi phản hồi kết hợp đến người dùng sử dụng phương thức send_message
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

# Hàm chính
def main():
    # Tạo ứng dụng bot
    application = Application.builder().token(bot_token).build()

    # Thêm trình xử lý lệnh /shopee
    application.add_handler(CommandHandler("shopee", handle_shopee_command))

    # Thêm trình xử lý lệnh /check
    application.add_handler(CommandHandler("check", handle_check_command))

    # Bắt đầu chạy bot
    application.run_polling()

if __name__ == "__main__":
    main()
