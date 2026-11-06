# 🛡️ RentGuard AI - 租屋合約智能守護系統

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Google GenAI SDK](https://img.shields.io/badge/AI-Gemini%203.5%20Flash%20Lite-8E75C2.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 專為台灣租屋族設計的 AI 法律顧問與合約審查系統。透過 Google Gemini 模型與內政部《住宅租賃定型化契約應記載及不得記載事項》法規比對，自動偵測不平等條款與違法霸王條款，並一鍵生成得體且堅定的 LINE 談判溝通草稿。

---

## ✨ 核心特色

- **多模態檔案支援**：
  - 支援 **PDF 合約**、**純文字合約 (.txt)**。
  - 支援 **圖片格式（PNG / JPG / JPEG）**，可直接上傳合約相片或房東的對話截圖進行視覺分析。
- **智慧合約防護機制（Guardrails）**：
  - 前置檢驗模組自動過濾非租屋相關檔案，避免無效運算與誤判。
- **三段式風險燈號分類（結構化 JSON 輸出）**：
  - 🔴 **高風險違法條文（紅燈）**：標記明顯違反法規、損害房客合法權益的條款（如苛扣押金、轉嫁修繕責任等）。
  - 🟡 **潛在不利條文（黃燈）**：辨識未直接違法但責任顯失衡平的風險條文。
  - 🟢 **合規條文（綠燈）**：標示符合內政部定型化契約之條文，保障雙方基本權益。
- **💬 擬真 LINE 談判草稿生成**：
  - 自動依據紅黃燈爭議點，生成語氣禮貌、依據明確且立場堅定的溝通範本，並支援一鍵複製，讓租客能直接與房東對話協商。
- **深色現代化儀表板**：
  - 基於 Streamlit 客製化 CSS，提供卡片式燈號分類與聊天室預覽介面。

---

## 🛠️ 技術棧 (Tech Stack)

- **核心語言**：Python 3.10+
- **前端介面**：[Streamlit](https://streamlit.io/)（搭配客製化 CSS 樣式元件）
- **AI 模型**：Google Gemini 3.5 Flash Lite (`google-genai` 官方 SDK)
- **檔案處理**：`pypdf`（PDF 文字萃取）
- **環境設定**：`python-dotenv`

---

## 🚀 快速開始

### 1. 取得專案原始碼

```bash
git clone [https://github.com/bensonchen07/rentguard-ai.git](https://github.com/bensonchen07/rentguard-ai.git)
cd rentguard-ai
