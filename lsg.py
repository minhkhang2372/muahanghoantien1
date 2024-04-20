import yaml
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests

# Đọc token từ bot_config.yml
with open("bot_config.yml", "r") as file:
    config = yaml.safe_load(file)
    bot_token = config["bot_token"]

# URL của API để lấy danh sách sản phẩm theo từ khóa
api_url_commission_keyword = "https://api.chietkhau.pro/api/v1/shopee/get-product-by-keyword"

# URL của API để lấy thông tin sản phẩm bằng liên kết
api_url_commission_link = "https://api.chietkhau.pro/api/v1/shopee/product-commission"

# URL của API để chuyển đổi liên kết
api_url_convert = "https://area08.000webhostapp.com/change_link/change.php"

# Hàm để gửi yêu cầu POST đến API và lấy danh sách sản phẩm theo từ khóa
def get_product_data_by_keyword(keyword):
    payload = {"keyword": keyword}
    response = requests.post(api_url_commission_keyword, data=payload)
    response.raise_for_status()
    return response.json()

# Hàm để gửi yêu cầu POST đến API và lấy thông tin sản phẩm bằng liên kết
def get_product_data_by_link(link):
    payload = {"link": link}
    response = requests.post(api_url_commission_link, data=payload)
    response.raise_for_status()
    return response.json()

# Hàm để chuyển đổi liên kết
def convert_link(content):
    user_cookie = "YOUR_USER_COOKIE_HERE"
    data = {"content": content, "userCookie": user_cookie}
    response = requests.post(api_url_convert, data=data)
    response.raise_for_status()
    return response.text

# Hàm xử lý lệnh /shopee của người dùng (tìm kiếm bằng tên sản phẩm)
def handle_shopee_command(update: Update, context: CallbackContext):
    args = context.args

    if len(args) == 0:
        update.message.reply_text("Vui lòng cung cấp từ khóa sản phẩm sau lệnh /shopee.")
        return

    keyword = args[0]

    product_data = get_product_data_by_keyword(keyword)

    if product_data.get("status") != "success":
        update.message.reply_text("Không lấy được dữ liệu sản phẩm!")
        return
    
    product_list = product_data.get("productList", [])
    top_5_products = product_list[:5]

    for product in top_5_products:
        product_name = product.get("productName", "")
        shop_name = product.get("shopName", "")
        price = product.get("price", "")
        commission = product.get("commission", "")
        product_link = product.get("productLink", "")

        converted_link = convert_link(product_link)

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

        update.message.reply_text(response_text)

# Hàm xử lý lệnh /check của người dùng (tìm kiếm bằng liên kết sản phẩm)
def handle_check_command(update: Update, context: CallbackContext):
    args = context.args

    if len(args) == 0:
        update.message.reply_text("Vui lòng cung cấp liên kết sản phẩm sau lệnh /check.")
        return
    
    product_link = args[0]

    product_data = get_product_data_by_link(product_link)

    converted_link = convert_link(product_link)

    response_text = "Không lấy được dữ liệu sản phẩm!" 

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

    update.message.reply_text(response_text)

def main():
    updater = Updater(bot_token, use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("shopee", handle_shopee_command))
    dispatcher.add_handler(CommandHandler("check", handle_check_command))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
