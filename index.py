import argparse
import random
from selenium_browserkit import BrowserManager, Node, By, Utility

PROJECT_URL = "https://app.prismax.ai"
MESSAGES = [
    "Loading, please wait...",
    "Processing your request...",
    "Download game https://usbgameretro.com",
    "Updating information, please wait...",
    "Working on it...",
    "Please wait a moment...",
    "Fetching content...",
    "Preparing data...",
    "Play game usbgameretro.com",
    "Retrieving information..."
]
class Setup:
    def __init__(self, node: Node, profile) -> None:
        self.node = node
        self.profile = profile
        
        self.run()

    def run(self):
        self.node.new_tab(f'{PROJECT_URL}', method="get", timeout=30)

class Auto:
    def __init__(self, node: Node, profile: dict) -> None:
        self.driver = node._driver
        self.node = node
        self.profile_name = profile.get('profile_name')
        self.email = profile.get('email')
        self.pwd_email = profile.get('pwd_email')

        self.run()
    
    def is_login(self):
        text = self.node.get_text(By.XPATH, "//span[contains(@class,'Dashboard_pointsValue')]")

        if text:
            if text == '...':
                self.node.log('⚠️ Chưa đăng nhập')
                return False
            else:
                self.node.log('✅ Đã đăng nhập')
                return True
        else:
            self.node.log('❌ Không thể xác nhận')

    def send_message(self):
        self.node.go_to(f'{PROJECT_URL}/live-control', timeout=15)
        if not self.node.find(By.XPATH, '//button[contains(text(),"Enter Live Control")]'):
            self.node.log('Không tìm thấy trang live')
            return False
        self.node.find_and_click(By.XPATH,'//button[contains(text(),"Live Chat")]')
        if not self.node.find_and_input(By.CSS_SELECTOR,'[data-teleop-chat-input="true"]', random.choice(MESSAGES)):
            self.node.log('Không tìm thấy input chat')
            return False
        self.node.find_and_click(By.XPATH,'//button[@type="submit" and not(@disabled)]')
        if self.node.find(By.XPATH,'//button[@type="submit" and @disabled]'):
            self.node.log('Gửi thành công')
            return True
        else:
            self.node.log('Gửi thất bại')
            return True

    def check_point(self):
        self.node.go_to(f'{PROJECT_URL}', timeout=30)
        return self.node.get_text(By.XPATH,"//span[contains(@class,'Dashboard_pointsValue')]")

    def run(self):
        self.node.new_tab(f'{PROJECT_URL}', timeout=30)
        if not self.is_login():
            self.node.snapshot('Chưa đăng nhập', stop=False)
        if not self.send_message():
            self.node.snapshot('Gửi tin nhắn thất bại', stop=False)
        point = self.check_point()
        self.node.snapshot(f'Hoàn thành công việc: {point} point', stop=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', action='store_true', help="Chạy ở chế độ tự động")
    parser.add_argument('--headless', action='store_true', help="Chạy trình duyệt ẩn")
    parser.add_argument('--disable-gpu', action='store_true', help="Tắt GPU")
    args = parser.parse_args()

    profiles = Utility.read_data('profile_name', 'email', 'pwd_email')
    max_profiles = Utility.read_config('MAX_PROFLIES')

    if not profiles:
        print("Không có dữ liệu để chạy")
        exit()

    browser_manager = BrowserManager(auto_handler=Auto, setup_handler=Setup)
    browser_manager.update_config(
                        headless=args.headless,
                        disable_gpu=args.disable_gpu,
                        use_tele=True
                    )
    # browser_manager.add_extensions('Meta-Wallet-*.crx','OKX-Wallet-*.crx')
    browser_manager.run_menu(
        profiles=profiles,
        max_concurrent_profiles=max_profiles,
        auto=args.auto
    )