import os
import requests
import pandas as pd
import logging
import warnings
import time
from functools import wraps
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import tkinter as tk
from tkinter import messagebox

# コーディング規約 12.2準拠: ログヘッダ定数
LOG_HEADER = "[経費登録_claude_sonnet_3.5.py]"

# ログ設定
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

@dataclass
class ExpenseItem:
    """経費項目データクラス（コーディング規約：わかりやすい名前）"""
    title: str
    category: str
    amount: int
    remarks: str = ""
    registration_code: Optional[str] = None

class BusinessRuleException(Exception):
    """ビジネスルール例外（コーディング規約 10.2準拠）"""
    pass

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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

class DataBackupService:
    """データ保存サービス（データ損失防止特性活用）"""
    
    def __init__(self, backup_file: str = "data_backup.xlsx"):
        self.backup_file = backup_file
        self._logger = logging.getLogger(__name__)
    
    def create_backup(self, df, sheet_name: str = "Sheet1") -> None:
        """一時保存実行"""
        try:
            df.to_excel(self.backup_file, sheet_name=sheet_name, index=False)
            self._logger.info(f"{LOG_HEADER} バックアップ作成: {self.backup_file}")
        except Exception as e:
            self._logger.warning(f"{LOG_HEADER} バックアップ作成失敗: {e}")

def create_edge_driver(options: webdriver.EdgeOptions) -> webdriver.Edge:
    """Selenium Manager（標準機能）のみを使用してEdgeドライバーを取得"""
    try:
        driver = webdriver.Edge(options=options)
        logging.info("[INFO] Selenium Managerを使用してEdgeドライバーを取得しました。")
        return driver
    except Exception as e:
        logging.error(f"[ERROR] Edgeドライバーの初期化に失敗しました: {e}")
        raise

def download_excel_if_not_exists():
    """data.xlsxが存在しない場合、ダウンロードする"""
    file_path = "data.xlsx"
    download_url = "https://www.expense-demo.com/data.xlsx"
    
    if not os.path.exists(file_path):
        logging.info("data.xlsx が存在しません。ダウンロードします。")
        try:
            response = requests.get(download_url)
            response.raise_for_status()
            with open(file_path, "wb") as f:
                f.write(response.content)
            logging.info("data.xlsx をダウンロードしました。")
        except Exception as e:
            logging.error(f"ダウンロード中にエラーが発生しました: {e}")
            raise
    else:
        logging.info("data.xlsx は既に存在します。")

# メインループ内での最適化
def setup_driver():
    """Edgeドライバーのセットアップ（手動配置不要）"""
    try:
        options = webdriver.EdgeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        return create_edge_driver(options)
    except Exception as e:
        logging.error(f"ドライバーのセットアップでエラーが発生しました: {e}")
        raise

def retry_on_stale_element(max_attempts: int = 3, delay: float = 1.0):
    """
    StaleElementReferenceException発生時のリトライデコレータ
    コーディング規約 10.6: リトライスコープ対応
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except StaleElementReferenceException as e:
                    if attempt == max_attempts - 1:
                        # ビジネスエラーとしてスロー
                        raise BusinessRuleException(f"要素参照エラー: {e}") from e
                    
                    logging.warning(f"{LOG_HEADER} 要素参照エラー (試行 {attempt + 1}/{max_attempts}): {e}")
                    time.sleep(delay)
                    continue
            return None
        return wrapper
    return decorator

def retry_on_stale(max_attempts=3, delay=1):
    """StaleElementReferenceException発生時のリトライデコレータ"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except StaleElementReferenceException:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

def safe_str(value):
    """値を安全に文字列に変換"""
    if pd.isna(value):
        return ""
    return str(value)

@retry_on_stale(max_attempts=3)
def click_button(driver, wait, locator):
    """ボタンクリックの共通処理"""
    button = wait.until(EC.element_to_be_clickable(locator))
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center', inline: 'center'});", button)
    # レイアウト安定を最短で待機
    driver.execute_script("window.requestAnimationFrame(()=>{})")
    button.click()
    return button

@retry_on_stale(max_attempts=3)
def input_text(driver, wait, locator, text):
    """テキスト入力の共通処理（最適化版）"""
    try:
        element = wait.until(EC.presence_of_element_located(locator))
        # スクロールは必要な場合のみ実行
        if not element.is_displayed():
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center', inline: 'center'});", element)
            driver.execute_script("window.requestAnimationFrame(()=>{})")
        
        # JavaScriptによる高速な入力
        driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input'));
            arguments[0].dispatchEvent(new Event('change'));
        """, element, str(text))
        return element
    except Exception as e:
        logging.error(f"入力処理でエラーが発生: {e}")
        raise

def go_back(driver, wait):
    """戻る処理の共通化"""
    back_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//a[text()='戻る']"))
    )
    back_button.click()
    # ページ遷移の完了を待機
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

# データ処理の最適化
def process_batch(driver, wait, df, batch_size=5):
    """バッチ処理による最適化"""
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        # バッチ単位でのバックアップ
        if i % (batch_size * 2) == 0:
            df.to_excel("data_backup.xlsx", sheet_name="Sheet1", index=False)

# データの事前検証
def validate_data(df):
    errors = []
    for index, row in df.iterrows():
        try:
            amount = int(row["金額"])
            if amount <= 0:
                errors.append(f"行 {index + 1}: 金額が不正です")
        except ValueError:
            errors.append(f"行 {index + 1}: 金額が数値ではありません")
    return errors

def main():
    try:
        # 開始時刻を記録
        start_time = time.time()
        start_datetime = time.strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"処理開始: {start_datetime}")
        
        # Excelファイルの確認とダウンロード
        download_excel_if_not_exists()
        
        # Excelファイルの読み込み
        try:
            df = pd.read_excel("data.xlsx", sheet_name="Sheet1")
            required_columns = ["タイトル", "種別", "金額", "備考"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"必要なカラムが見つかりません: {', '.join(missing_columns)}")
        except Exception as e:
            raise Exception(f"Excelファイルの読み込みに失敗しました: {e}")
        
        # 「番号」列が存在しない場合は作成し、型をobjectに設定
        if "番号" not in df.columns:
            df["番号"] = pd.NA
        df["番号"] = df["番号"].astype("object")

        # データの事前検証
        validation_errors = validate_data(df)
        if validation_errors:
            error_message = "以下のエラーがあります:\n" + "\n".join(validation_errors)
            raise ValueError(error_message)
        
        # ブラウザの設定
        driver = setup_driver()
        wait = WebDriverWait(driver, 10)
        
        # Webサイトにアクセス
        driver.get("https://www.expense-demo.com/")
        
        # 「経費を登録する」ボタンをクリック（リトライ機能付き）
        try:
            click_button(driver, wait, (By.XPATH, "//a[text()='経費を登録する']"))
        except TimeoutException:
            logging.warning("'経費を登録する'ボタンが見つかりません。ページを更新して再試行します。")
            driver.refresh()
            click_button(driver, wait, (By.XPATH, "//a[text()='経費を登録する']"))

        # 各行のデータを処理
        processed_count = 0
        for index, row in df.iterrows():
            try:
                # 「明細を登録する」ボタンをクリック（リトライ機能付き）
                try:
                    click_button(driver, wait, (By.ID, "newTx"))
                except TimeoutException:
                    logging.warning(f"行 {index + 1}: '明細を登録する'ボタンが見つかりません。ページを更新して再試行します。")
                    driver.refresh()
                    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
                    click_button(driver, wait, (By.ID, "newTx"))
                
                # タイトル入力（必須項目）
                title = safe_str(row["タイトル"])
                if not title:
                    raise ValueError("タイトルは必須項目です")
                try:
                    input_text(driver, wait, (By.ID, "ledger_ledger_name"), title)
                except TimeoutException:
                    logging.warning(f"行 {index + 1}: タイトル入力フィールドが見つかりません。再試行します。")
                    driver.refresh()
                    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
                    click_button(driver, wait, (By.ID, "newTx"))
                    input_text(driver, wait, (By.ID, "ledger_ledger_name"), title)
                
                # 種別選択（必須項目）
                expense_type = safe_str(row["種別"])
                if not expense_type:
                    raise ValueError("種別は必須項目です")
                try:
                    type_select = Select(wait.until(
                        EC.presence_of_element_located((By.TAG_NAME, "SELECT"))
                    ))
                    type_select.select_by_visible_text(expense_type)
                except TimeoutException:
                    logging.warning(f"行 {index + 1}: 種別選択フィールドが見つかりません。再試行します。")
                    driver.refresh()
                    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
                    click_button(driver, wait, (By.ID, "newTx"))
                    input_text(driver, wait, (By.ID, "ledger_ledger_name"), title)
                    type_select = Select(wait.until(
                        EC.presence_of_element_located((By.TAG_NAME, "SELECT"))
                    ))
                    type_select.select_by_visible_text(expense_type)
                
                # 金額入力（必須項目）
                try:
                    amount = int(row["金額"])
                    if amount <= 0:
                        raise ValueError("金額は正の数である必要があります")
                    # 金額を文字列に変換して一括入力
                    input_text(driver, wait, (By.ID, "ledger_cost"), str(amount))
                except (ValueError, TypeError) as e:
                    raise ValueError(f"金額の入力でエラーが発生しました: {e}")
                
                # 備考入力（オプション）
                try:
                    input_text(driver, wait, (By.ID, "ledger_remarks"), safe_str(row["備考"]))
                except TimeoutException:
                    logging.warning(f"行 {index + 1}: 備考入力フィールドが見つかりません。再試行します。")
                    driver.refresh()
                    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
                    # 前のフィールドをすべて再入力
                    click_button(driver, wait, (By.ID, "newTx"))
                    input_text(driver, wait, (By.ID, "ledger_ledger_name"), title)
                    type_select = Select(wait.until(
                        EC.presence_of_element_located((By.TAG_NAME, "SELECT"))
                    ))
                    type_select.select_by_visible_text(expense_type)
                    input_text(driver, wait, (By.ID, "ledger_cost"), str(amount))
                    input_text(driver, wait, (By.ID, "ledger_remarks"), safe_str(row["備考"]))
                
                # 登録ボタンクリック
                try:
                    click_button(driver, wait, (By.XPATH, "//input[@type='submit' and @value='登録する']"))
                except TimeoutException:
                    logging.warning(f"行 {index + 1}: 登録ボタンが見つかりません。再試行します。")
                    # 全フィールドを再入力
                    driver.refresh()
                    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
                    click_button(driver, wait, (By.ID, "newTx"))
                    input_text(driver, wait, (By.ID, "ledger_ledger_name"), title)
                    type_select = Select(wait.until(
                        EC.presence_of_element_located((By.TAG_NAME, "SELECT"))
                    ))
                    type_select.select_by_visible_text(expense_type)
                    input_text(driver, wait, (By.ID, "ledger_cost"), str(amount))
                    input_text(driver, wait, (By.ID, "ledger_remarks"), safe_str(row["備考"]))
                    click_button(driver, wait, (By.XPATH, "//input[@type='submit' and @value='登録する']"))

                # 登録完了まで待機し、コードを取得
                # ページ遷移完了を待機
                wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

                extracted_code = None
                code_locators = [
                    (By.XPATH, "//dd[1]"),
                    (By.XPATH, "//strong[text()='コード:']/following-sibling::*[1]"),
                    (By.XPATH, "//strong[contains(text(), 'コード')]/following-sibling::dd"),
                    (By.XPATH, "//dt[contains(text(), 'コード')]/following-sibling::dd[1]")
                ]
                
                for locator in code_locators:
                    try:
                        element = wait.until(EC.presence_of_element_located(locator))
                        text = element.text.strip()
                        if text:
                            extracted_code = text
                            logging.info(f"行 {index + 1}: コード '{extracted_code}' を取得しました。")
                            break
                    except TimeoutException:
                        continue  # 次のセレクタを試す
                
                if not extracted_code:
                    logging.warning(f"行 {index + 1}: 登録コードの取得に失敗しました。")

                # Excelに書き込み
                if extracted_code:
                    df.loc[index, "番号"] = extracted_code
                
                # 一時保存（エラー発生時のデータ損失を防ぐ）
                processed_count += 1
                if processed_count % 10 == 0:
                    df.to_excel("data_backup.xlsx", sheet_name="Sheet1", index=False)
                    logging.info(f"{LOG_HEADER} バックアップ保存（{processed_count}件処理）")
                
                # 戻るボタンクリック
                back_locators = [
                    (By.LINK_TEXT, "戻る"),
                    (By.XPATH, "//a[text()='戻る']"),
                    (By.XPATH, "//a[contains(text(), '戻る')]"),
                    (By.XPATH, "//button[text()='戻る']")
                ]
                
                back_button_clicked = False
                for locator in back_locators:
                    try:
                        button = wait.until(EC.element_to_be_clickable(locator))
                        button.click()
                        back_button_clicked = True
                        logging.info(f"行 {index + 1}: 戻るボタンをクリックしました。")
                        break
                    except TimeoutException:
                        continue

                if not back_button_clicked:
                    logging.warning(f"行 {index + 1}: 戻るボタンが見つかりません。ページを更新します。")
                    driver.refresh()
                
                # 戻る/更新後の待機
                wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
                    
            except Exception as e:
                logging.error(f"行 {index + 1} の処理中にエラーが発生しました: {e}")
                # エラーリカバリー処理
                logging.info(f"行 {index + 1}: エラーリカバリーを試行します...")
                try:
                    # 現在のURLを確認
                    current_url = driver.current_url
                    logging.info(f"現在のURL: {current_url}")
                    
                    # エラーページかフォーム入力ページの場合は一覧画面に戻る
                    if 'error' in current_url.lower() or 'new' in current_url.lower() or 'edit' in current_url.lower():
                        logging.info("一覧画面に戻ります...")
                        # JavaScriptによる履歴操作を試行
                        driver.execute_script("window.history.go(-1);")
                        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
                        
                        # 画面遷移の完了を待機
                        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
                except Exception as recovery_error:
                    logging.error(f"エラーリカバリーに失敗しました: {recovery_error}")
                continue

        # Excelファイルの保存
        df.to_excel("data.xlsx", sheet_name="Sheet1", index=False)
        
        # 終了時刻と処理時間を計算
        end_time = time.time()
        end_datetime = time.strftime("%Y-%m-%d %H:%M:%S")
        process_time = end_time - start_time
        hours = int(process_time // 3600)
        minutes = int((process_time % 3600) // 60)
        seconds = int(process_time % 60)
        
        # 処理時間の文字列を作成
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # 完了メッセージの表示
        root = tk.Tk()
        root.withdraw()
        message = (
            f"経費登録処理が完了しました。\n\n"
            f"開始時刻: {start_datetime}\n"
            f"終了時刻: {end_datetime}\n"
            f"処理時間: {time_str}"
        )
        messagebox.showinfo("処理完了", message)
        root.destroy()
        
        # メッセージ確認後にブラウザを閉じる
        logging.info("ブラウザを終了します...")
        driver.quit()
        
    except Exception as e:
        logging.error(f"予期せぬエラーが発生しました: {e}")
        # エラーメッセージを表示
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("エラー", f"エラーが発生しました: {e}")
        root.destroy()
        
        # エラーメッセージ確認後にブラウザを閉じる
        if 'driver' in locals():
            logging.info("ブラウザを終了します...")
            driver.quit()

if __name__ == "__main__":
    main()
