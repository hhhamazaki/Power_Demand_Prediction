import os
import requests
import pandas as pd
import openpyxl
import tkinter.messagebox as msgbox
import logging
import warnings
from datetime import datetime

# WebDriverManagerのログを完全に抑制
warnings.filterwarnings("ignore")
logging.getLogger('WDM').setLevel(logging.CRITICAL)
logging.getLogger('webdriver_manager').setLevel(logging.CRITICAL)
logging.getLogger('selenium').setLevel(logging.ERROR)
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except:
    pass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# 最終メッセージ確認後に閉じるためのドライバ参照
_LAST_DRIVER = None

def create_edge_driver(options: webdriver.EdgeOptions) -> webdriver.Edge:
    """Selenium Manager（標準機能）のみを使用してEdgeドライバーを取得"""
    try:
        driver = webdriver.Edge(options=options)
        logging.info("Selenium Managerを使用してEdgeドライバーを取得しました。")
        return driver
    except Exception as e:
        logging.error(f"Edgeドライバーの初期化に失敗しました: {e}")
        raise

CONFIG = {
    'DOWNLOAD_URL': 'https://www.expense-demo.com/data.xlsx',
    'TARGET_URL': 'https://www.expense-demo.com/',
    'EXCEL_FILE': 'data.xlsx',
    'SHEET_NAME': 'Sheet1',
    'TIMEOUT': 15,
    'RETRY_COUNT': 3
}

import os
log_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(log_dir, 'expense_automation.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# --- 安全操作ユーティリティ（フォールバック含む） ---
def safe_click(driver, wait, locator, name="要素", timeout=None):
    try:
        element = wait.until(EC.element_to_be_clickable(locator))
        element.click()
        logging.info(f"{name} をクリック")
        return True
    except TimeoutException:
        logging.warning(f"{name} が見つからない/クリック不可（タイムアウト）")
        return False
    except Exception as e:
        logging.error(f"{name} のクリックでエラー: {e}")
        return False

def safe_input(wait, locator, text, name="入力フィールド"):
    try:
        el = wait.until(EC.presence_of_element_located(locator))
        el.clear()
        el.send_keys("" if text is None else str(text))
        logging.info(f"{name} に入力")
        return True
    except TimeoutException:
        logging.warning(f"{name} が見つからない（タイムアウト）")
        return False
    except Exception as e:
        logging.error(f"{name} の入力でエラー: {e}")
        return False

def safe_select(wait, locator, value, name="選択フィールド"):
    try:
        sel_el = wait.until(EC.presence_of_element_located(locator))
        Select(sel_el).select_by_visible_text("" if value is None else str(value))
        logging.info(f"{name} で '{value}' を選択")
        return True
    except TimeoutException:
        logging.warning(f"{name} が見つからない（タイムアウト）")
        return False
    except Exception as e:
        logging.error(f"{name} の選択でエラー: {e}")
        return False

def get_text_safe(wait, locator, name="テキスト要素"):
    try:
        el = wait.until(EC.presence_of_element_located(locator))
        txt = el.text.strip()
        logging.info(f"{name} から '{txt}' を取得")
        return txt
    except Exception:
        return None

def check_and_download_file():
    file_path = CONFIG['EXCEL_FILE']
    try:
        if os.path.exists(file_path):
            logging.info("ファイルが存在します。")
            print("ファイルが存在します。")
            return True
        else:
            logging.info("ファイルが存在しないため、ダウンロードを開始します。")
            print("ファイルが存在しないため、ダウンロードを開始します。")
            try:
                response = requests.get(CONFIG['DOWNLOAD_URL'], timeout=30)
                response.raise_for_status()
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                logging.info("ファイルのダウンロードが完了しました。")
                print("ファイルのダウンロードが完了しました。")
                return True
            except Exception as net_error:
                logging.warning(f"ファイルのダウンロードに失敗しました: {net_error}")
                print(f"ファイルのダウンロードに失敗しました: {net_error}")
                return False
    except Exception as e:
        error_msg = f"ファイル処理でエラーが発生しました: {e}"
        logging.error(error_msg)
        print(f"エラー: {error_msg}")
        return False

def format_time_duration(start_time, end_time):
    duration = end_time - start_time
    total_seconds = int(duration.total_seconds())
    if total_seconds < 60:
        return f"{total_seconds}秒"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}分{seconds}秒"
    else:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours}時間{minutes}分{seconds}秒"

def show_processing_summary(start_time, end_time, success_count, total_count, errors=None):
    duration_str = format_time_duration(start_time, end_time)
    title = "経費登録処理完了"
    error_count = 0
    if errors:
        if isinstance(errors, str):
            error_count = errors.count('\n') + 1 if errors.strip() else 0
        elif isinstance(errors, list):
            error_count = len(errors)
    success_str = f"成功: {success_count}件"
    fail_str = f"失敗: {error_count}件"
    message = f"""処理が完了しました。\n\n開始時刻: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n終了時刻: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n処理時間: {duration_str}\n\n処理結果: {success_str} / {total_count}件 ({fail_str})"""
    if error_count > 0:
        if isinstance(errors, list):
            error_text = '\n'.join(errors)
        else:
            error_text = str(errors)
        message += f"\n\nエラー詳細(先頭のみ):\n{error_text[:200]}..."
    msgbox.showinfo(title, message)

def excel_processing():
    try:
        df = pd.read_excel(CONFIG['EXCEL_FILE'], sheet_name=CONFIG['SHEET_NAME'])
        workbook = openpyxl.load_workbook(CONFIG['EXCEL_FILE'])
        worksheet = workbook[CONFIG['SHEET_NAME']]
        result = web_processing(df, workbook, worksheet)
        workbook.save(CONFIG['EXCEL_FILE'])
        workbook.close()
        return result
    except Exception as e:
        logging.error(f"Excel処理エラー: {e}")
        raise

def web_processing(df, workbook, worksheet):
    options = webdriver.EdgeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option('useAutomationExtension', False)

    global _LAST_DRIVER
    driver = None
    try:
        # Selenium Manager（標準機能）のみを使用
        driver = create_edge_driver(options)
        _LAST_DRIVER = driver
        wait = WebDriverWait(driver, CONFIG['TIMEOUT'])
        driver.maximize_window()
        driver.get(CONFIG['TARGET_URL'])

        # 初回「経費を登録する」フォールバック付き
        open_locators = [
            (By.LINK_TEXT, "経費を登録する"),
            (By.XPATH, "//a[text()='経費を登録する']"),
            (By.XPATH, "//a[contains(@class,'menu-link') and contains(normalize-space(),'経費を登録する')]")
        ]
        if not any(safe_click(driver, wait, loc, "経費を登録するボタン") for loc in open_locators):
            raise Exception("初期メニューのクリックに失敗")

        result = process_excel_rows(driver, wait, df, worksheet)
        return result
    except Exception as e:
        # 失敗時スクリーンショット
        try:
            if driver:
                from datetime import datetime as _dt
                png = f"error_screenshot_{_dt.now().strftime('%Y%m%d_%H%M%S')}.png"
                driver.save_screenshot(png)
                logging.error(f"スクリーンショット保存: {png}")
        except Exception:
            pass
    raise

def process_excel_rows(driver, wait, df, worksheet):
    success_count = 0
    total_count = len(df)
    errors = []
    for index, row in df.iterrows():
        try:
            title = str(row['タイトル'])
            category = str(row['種別'])
            amount = str(row['金額'])
            remarks = str(row['備考']) if pd.notna(row['備考']) else ""
            excel_row = index + 2
            registration_code = register_expense_item(driver, wait, title, category, amount, remarks)
            worksheet.cell(row=excel_row, column=5, value=registration_code if registration_code else "ERROR")
            if registration_code:
                success_count += 1
            else:
                errors.append(f"行 {index + 1}: 登録コード取得に失敗")
        except Exception as e:
            logging.error(f"行 {index + 1} の処理でエラー: {e}")
            errors.append(f"行 {index + 1}: {e}")
            continue
    return success_count, total_count, errors

def register_expense_item(driver, wait, title, category, amount, remarks):
    # 明細追加
    if not safe_click(driver, wait, (By.ID, "newTx"), "明細を登録するボタン"):
        if not safe_click(driver, wait, (By.LINK_TEXT, "明細を登録する"), "明細を登録するボタン"):
            raise Exception("明細追加ボタンが見つかりません")

    # 入力
    if not safe_input(wait, (By.ID, "ledger_ledger_name"), title, "タイトルフィールド"):
        raise Exception("タイトル入力に失敗")

    # 種別セレクト（候補順）
    select_locators = [
        (By.CSS_SELECTOR, "select"),
        (By.XPATH, "//select[1]"),
    ]
    if not any(safe_select(wait, loc, category, "種別フィールド") for loc in select_locators):
        logging.warning("種別の選択に失敗（処理は継続）")

    # 金額・備考
    if not safe_input(wait, (By.ID, "ledger_cost"), amount, "金額フィールド"):
        raise Exception("金額入力に失敗")
    if not safe_input(wait, (By.ID, "ledger_remarks"), remarks, "備考フィールド"):
        logging.warning("備考入力に失敗（任意項目）")

    # 登録実行
    submit_locators = [
        (By.XPATH, "//input[@type='submit' and @value='登録する']"),
        (By.CSS_SELECTOR, "input[type='submit']"),
        (By.XPATH, "//button[normalize-space()='登録する']")
    ]
    if not any(safe_click(driver, wait, loc, "登録ボタン") for loc in submit_locators):
        raise Exception("登録ボタンのクリックに失敗")

    # コード取得（フォールバック）
    code_locators = [
        (By.XPATH, "//dd[1]"),
        (By.XPATH, "//strong[text()='コード:']/following-sibling::*[1]"),
        (By.XPATH, "//dt[contains(text(),'コード')]/following-sibling::dd[1]")
    ]
    registration_code = None
    for loc in code_locators:
        registration_code = get_text_safe(wait, loc, "登録コード")
        if registration_code:
            break

    # 戻る
    back_locators = [
        (By.LINK_TEXT, "戻る"),
        (By.XPATH, "//a[text()='戻る']"),
        (By.XPATH, "//button[text()='戻る']")
    ]
    any(safe_click(driver, wait, loc, "戻るボタン") for loc in back_locators)

    return registration_code

def main():
    global _LAST_DRIVER
    start_time = datetime.now()
    try:
        if not check_and_download_file():
            return
        success_count, total_count, errors = 0, 0, []
        try:
            result = excel_processing()
            if result is not None:
                success_count, total_count, errors = result
        except Exception as e:
            logging.error(f"全体処理エラー: {e}")
            # エラーも最終メッセージとして扱い、その後にブラウザを閉じる
            msgbox.showerror("エラー", f"処理中にエラーが発生しました: {e}")
            return
        end_time = datetime.now()
        # 最終サマリー（OK押下までブロッキング）
        show_processing_summary(start_time, end_time, success_count, total_count, errors)
    except Exception as e:
        logging.error(f"致命的エラー: {e}")
        msgbox.showerror("エラー", f"致命的エラー: {e}")
    finally:
        # 最終メッセージ確認後にブラウザを閉じる
        if _LAST_DRIVER is not None:
            try:
                _LAST_DRIVER.quit()
                logging.info("WebDriver を終了しました")
            except Exception:
                pass

if __name__ == "__main__":
    main()
