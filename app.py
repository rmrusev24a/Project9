import streamlit as st
import easyocr
import numpy as np
from PIL import Image, ImageEnhance
 
harmful_e_numbers = {
    "E407": "Карагенан — възпаления, храносмилателни проблеми",
    "E621": "Натриев глутамат — главоболие, алергии",
    "E262": "Натриев ацетат — дразни стомаха",
    "E300": "Аскорбинова киселина — в големи дози дразни стомаха",
    "E330": "Лимонена киселина — уврежда зъбния емайл",
    "E250": "Натриев нитрит — риск от онкологични заболявания",
    "E952": "Цикламат — подсладител, забранен в някои страни",
    "E471": "Емулгатор — може да наруши чревната микробиота",
    "E472": "Емулгатор — може да наруши чревната микробиота",
    "E450": "Дифосфати — нарушават калциево-фосфорния баланс",
    "E621": "Мононатриев глутамат (MSG) — главоболие, сърцебиене",
    "E102": "Тартразин — хиперактивност при деца, алергии",
    "E110": "Жълто залез — алергии, хиперактивност",
    "E124": "Понсо 4R — алергии, забранен в САЩ",
    "E129": "Алура червено — хиперактивност при деца",
    "E133": "Брилянтно синьо — алергии",
    "E220": "Серен диоксид — алергии, астма",
    "E221": "Натриев сулфит — алергии, астма",
    "E320": "BHA — потенциално канцерогенен",
    "E951": "Аспартам — спорно влияние върху здравето",
}
 
harmful_words = {
    "палмово масло": "Насищени мазнини — вредно за сърцето",
    "хидрогенирано": "Трансмазнини — вредни за сърдечно-съдовата система",
    "фруктозен сироп": "Високо фруктозен царевичен сироп — затлъстяване, диабет",
    "фосфат": "Фосфати — могат да влияят негативно на бъбреците",
    "нитрат": "Нитрати — риск от канцерогени при преработка",
    "нитрит": "Нитрити — риск от онкологични заболявания",
    "консерван": "Консерванти — често съдържат нитрати или сулфити",
    "лактоза": "Лактоза — може да причини стомашен дискомфорт при непоносимост",
    "глутен": "Глутен — проблемен при целиакия и непоносимост",
    "аспартам": "Аспартам — изкуствен подсладител, спорно влияние",
}
 
food_alternatives = {
    "палмово масло": ["Зехтин или слънчогледово масло", "Кокосово масло в малки количества"],
    "хидрогенирано": ["Масло, зехтин или авокадо като източници на мазнини"],
    "нитрит": ["Прясно месо без добавки", "Домашно приготвени продукти"],
    "нитрат": ["Органични меса без консерванти"],
    "фруктозен сироп": ["Мед или кленов сироп", "Пресни плодове за подслаждане"],
    "аспартам": ["Стевия като натурален подсладител", "Мед или кокосова захар"],
    "лактоза": ["Растителни млека — бадемово, овесено, соево"],
    "глутен": ["Ориз, царевица, елда, киноа"],
}
 
def enhance_image(img):
    img = img.convert("RGB")
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.0)
    return img
 
def extract_text(img):
    reader = easyocr.Reader(["bg", "en"], gpu=False)
    img_array = np.array(img)
    results = reader.readtext(img_array, detail=0)
    return " ".join(results)
 
def find_harmful(text):
    text_upper = text.upper()
    text_lower = text.lower()
    found_e = {}
    found_words = {}
 
    for code, description in harmful_e_numbers.items():
        if code.upper() in text_upper:
            found_e[code] = description
 
    for word, description in harmful_words.items():
        if word.lower() in text_lower:
            found_words[word] = description
 
    return found_e, found_words
 
def get_alternatives(found_words):
    alternatives = []
    for word in found_words:
        if word in food_alternatives:
            alternatives.extend(food_alternatives[word])
    return list(set(alternatives))
 
st.set_page_config(page_title="Анализатор на етикети", page_icon="🔬", layout="centered")
 
st.title("🔬 OCR етикет + вредни съставки + алтернатива")
st.markdown("Качи снимка на хранителен етикет и ще открием вредните съставки.")
 
uploaded_file = st.file_uploader("Качи изображение на етикет:", type=["jpg", "jpeg", "png", "webp"])
camera_photo = st.camera_input("Или направи снимка с камера:")
 
image = None
if uploaded_file:
    image = Image.open(uploaded_file)
elif camera_photo:
    image = Image.open(camera_photo)
 
if image:
    st.image(image, caption="Качено изображение", use_container_width=True)
 
    with st.spinner("Четем етикета с AI (EasyOCR)..."):
        enhanced = enhance_image(image)
        text = extract_text(enhanced)
 
    st.subheader("📄 Разпознат текст:")
    st.text_area("", text, height=150)
 
    found_e, found_words = find_harmful(text)
 
    st.subheader("🧪 Открити вредни съставки (Е-кодове):")
    if found_e:
        for code, desc in found_e.items():
            st.error(f"⚠️ **{code}** — {desc}")
    else:
        st.success("✅ Няма открити Е-номера.")
 
    st.subheader("🍬 Засечени съставки (по дума):")
    if found_words:
        for word, desc in found_words.items():
            st.warning(f"⚠️ {word} — {desc}")
    else:
        st.success("✅ Няма засечени проблемни съставки.")
 
    alternatives = get_alternatives(found_words)
    if alternatives:
        st.subheader("🍽️ Алтернативи:")
        for alt in alternatives:
            st.info(f"✔️ {alt}")
 
    report_lines = ["=== ОТЧЕТ ЗА АНАЛИЗ НА ЕТИКЕТ ===\n"]
    report_lines.append("--- Разпознат текст ---\n" + text + "\n")
    report_lines.append("\n--- Вредни Е-номера ---\n")
    for k, v in found_e.items():
        report_lines.append(f"{k}: {v}\n")
    report_lines.append("\n--- Вредни съставки ---\n")
    for k, v in found_words.items():
        report_lines.append(f"{k}: {v}\n")
    report_lines.append("\n--- Алтернативи ---\n")
    for a in alternatives:
        report_lines.append(f"- {a}\n")
 
    report_text = "".join(report_lines)
    st.subheader("📥 Генериран отчет")
    st.download_button("⬇️ Изтегли отчет като .txt", data=report_text, file_name="report.txt", mime="text/plain")
