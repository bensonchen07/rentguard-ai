import streamlit as st
import os
import time
from dotenv import load_dotenv
from google import genai

# 載入環境變數
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 頁面基本設定
st.set_page_config(page_title="RentGuard AI 租事順利", page_icon="🛡️", layout="wide")

st.title("🛡️ 租事順利 RentGuard AI")
st.subheader("租屋合約 AI 即時健檢與法律防禦系統（Gemini 驅動）")
st.markdown("---")

# 定義安全呼叫 Gemini API 的輔助函式 (含 503 自動重試保護)
def generate_content_with_retry(client, model_name, contents, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents
            )
            return response
        except Exception as e:
            if "503" in str(e) and attempt < max_retries - 1:
                time.sleep(2)  # 等待 2 秒後自動重試
                continue
            else:
                raise e

# ==================== 側邊欄：快速 AI 狀態與連線測試 ====================
st.sidebar.header("🛠️ 開發者測試面板")
st.sidebar.markdown("點擊下方按鈕，測試 API 連線：")

if st.sidebar.button("⚡ 測試 Gemini API 連線"):
    if not api_key:
        st.sidebar.error("❌ 錯誤：找不到 GEMINI_API_KEY，請檢查 .env 檔！")
    else:
        try:
            with st.spinner("正在向 Gemini 3.5 Flash-Lite 發送測試請求..."):
                client = genai.Client(api_key=api_key)
                response = generate_content_with_retry(
                    client,
                    model_name='gemini-3.5-flash-lite',
                    contents="請回覆：'Gemini 3.5 Flash-Lite API 連線測試成功！' 並且打個招呼。"
                )
                st.sidebar.success(response.text)
        except Exception as e:
            st.sidebar.error(f"❌ 連線失敗，錯誤訊息：\n{e}")

# ==================== 主畫面：合約上傳與健檢 ====================
st.header("1. 上傳合約文件")
uploaded_file = st.file_uploader("請上傳租屋合約（支援 PDF 格式）", type=["pdf"])

if uploaded_file is not None:
    st.success(f"成功接收檔案：{uploaded_file.name}")
    
    # 分析按鈕
    if st.button("🚀 開始 Gemini 合約深度健檢", type="primary"):
        if not api_key:
            st.error("找不到 GEMINI_API_KEY，請檢查 `.env` 檔案是否設定正確！")
        else:
            with st.spinner("Gemini 正在原生解析 PDF 並對照內政部《住宅租賃定型化契約》中..."):
                try:
                    client = genai.Client(api_key=api_key)
                    
                    # 暫存 PDF 檔案
                    temp_pdf_path = "temp_contract.pdf"
                    with open(temp_pdf_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # 上傳給 Gemini
                    uploaded_doc = client.files.upload(file=temp_pdf_path)

                    # 提示詞
                    prompt = (
                        "你是一位專業的台灣房地產法律顧問與AI合約分析師。"
                        "請根據台灣內政部頒布的《住宅租賃定型化契約應約定及不得約定事項》，"
                        "對上傳的租約內容進行嚴格審查。"
                        "請找出其中的違法條款、高風險陷阱（如修繕責任轉嫁、違約金過高、水電費超收等）。"
                        "請以繁體中文回答，並結構化輸出："
                        "1. 🔴 紅燈高風險條款"
                        "2. 🟡 黃燈注意事項"
                        "3. 🟢 綠燈符合規範"
                        "4. 💡 一鍵LINE談判溝通草稿"
                    )

                    response = generate_content_with_retry(
                        client,
                        model_name='gemini-3.5-flash-lite',
                        contents=[uploaded_doc, prompt]
                    )

                    # 清理暫存檔
                    if os.path.exists(temp_pdf_path):
                        os.remove(temp_pdf_path)

                    # 顯示分析結果
                    st.markdown("---")
                    st.header("2. AI 風險檢測報告")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"呼叫 Gemini API 時發生錯誤：{e}")