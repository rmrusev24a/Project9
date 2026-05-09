import streamlit as st
import easyocr
import numpy as np
from PIL import Image, ImageEnhance
from io import BytesIO
import re
import os
 
# -------------------------------------------------------------------
# БАЗА С Е-та
# -------------------------------------------------------------------
harmful_db = {
    "e100": ("Куркумин – натурален оцветител", 1),
    "e102": ("Тартразин – синтетичен оцветител, алергии при деца", 2),
    "e110": ("Залез жълто – алерген, забранен в някои страни", 2),
    "e120": ("Кармин – от насекоми, алерген", 1),
    "e122": ("Кармуазин – синтетичен оцветител, алерген", 2),
    "e124": ("Понсо – синтетичен оцветител, алерген", 2),
    "e129": ("Алура червено – хиперактивност при деца", 2),
    "e162": ("Бетанин – натурален оцветител от цвекло, безопасен", 1),
    "e202": ("Калиев сорбат – консервант, може да дразни кожата", 1),
    "e210": ("Бензоена киселина – консервант, алерген", 2),
    "e211": ("Натриев бензоат – може да причини хиперактивност", 2),
    "e220": ("Серен диоксид – алерген, вреден за астматици", 2),
    "e250": ("Натриев нитрит – риск от рак при прекомерна употреба", 3),
    "e251": ("Натриев нитрат – превръща се в нитрит в тялото", 2),
    "e262": ("Натриев ацетат – дразни стомаха при чувствителни хора", 1),
    "e290": ("Въглероден диоксид – опаковъчен газ, безопасен", 1),
    "e300": ("Аскорбинова киселина (витамин C) – антиоксидант, безопасен", 1),
    "e330": ("Лимонена киселина – уврежда зъбния емайл при прекомерна употреба", 1),
    "e331": ("Натриев цитрат – регулатор на киселинност, безопасен", 1),
    "e407": ("Карагенан – може да причини възпаления в червата", 2),
    "e420": ("Сорбитол – в големи количества причинява диария", 1),
    "e450": ("Дифосфати – нарушава калциево-фосфорния баланс, рискови за бъбреците", 2),
    "e451": ("Трифосфати – подобни рискове като Е450", 2),
    "e452": ("Полифосфати – подобни рискове като Е450", 2),
    "e471": ("Моно- и диглицериди – емулгатор, обикновено безопасен", 1),
    "e472": ("Естери на мастни киселини – емулгатор", 1),
    "e476": ("Полирицинолеат – емулгатор в шоколад, спорен при деца", 1),
    "e500": ("Натриев карбонат – набухвател, безопасен", 1),
    "e621": ("Мононатриев глутамат (MSG) – главоболие и сърцебиене при чувствителни", 2),
    "e941": ("Азот – опаковъчен газ, безопасен", 1),
    "e950": ("Ацесулфам К – изкуствен подсладител, спорен", 2),
    "e951": ("Аспартам – спорен подсладител, противоречиви изследвания", 2),
    "e952": ("Цикламат – забранен в САЩ, спорен подсладител", 2),
    "e954": ("Захарин – спорен изкуствен подсладител", 2),
    "e955": ("Сукралоза – може да влияе на чревната флора", 1),
}
 
def get_category(num):
    e = int(num)
    if 100 <= e <= 199: return "Оцветител"
    elif 200 <= e <= 299: return "Консервант"
    elif 300 <= e <= 399: return "Антиоксидант"
    elif 400 <= e <= 499: return "Сгъстител / стабилизатор"
    elif 500 <= e <= 599: return "Регулатор на киселинност"
    elif 600 <= e <= 699: return "Подобрител на вкус"
    elif 900 <= e <= 999: return "Подсладител / газ / глазиращ агент"
    elif 1000 <= e <= 1520: return "Други добавки"
    else: return "Неизвестно"
 
# -------------------------------------------------------------------
# УМНА ОБРАБОТКА НА СНИМКАТА
# -------------------------------------------------------------------
def detect_image_type(img_rgb):
    arr = np.array(img_rgb)
    r = arr[:,:,0].astype(int)
    g = arr[:,:,1].astype(int)
    b = arr[:,:,2].astype(int)
    color_diff = (np.abs(r - g) + np.abs(g - b) + np.abs(r - b)).mean()
    return "bw" if color_diff < 25 else "color"
 
def otsu_threshold(gray_arr):
    hist = np.bincount(gray_arr.flatten(), minlength=256)
    total = gray_arr.size
    best_thresh, best_var = 128, 0
    for t in range(1, 255):
        w0 = hist[:t].sum() / total
        w1 = hist[t:].sum() / total
        if w0 == 0 or w1 == 0:
            continue
        mu0 = (hist[:t] * np.arange(t)).sum() / (hist[:t].sum() + 1e-10)
        mu1 = (hist[t:] * np.arange(t, 256)).sum() / (hist[t:].sum() + 1e-10)
        var = w0 * w1 * (mu0 - mu1) ** 2
        if var > best_var:
            best_var = var
            best_thresh = t
    return best_thresh
 
def preprocess_image(img):
    img_rgb = img.convert("RGB")
    img_type = detect_image_type(img_rgb)
    arr = np.array(img_rgb)
 
    if img_type == "color":
        r = arr[:,:,0].astype(int)
        g = arr[:,:,1].astype(int)
        b = arr[:,:,2].astype(int)
        # червен фон
        red_mask = (r - g > 60) & (r - b > 60) & (arr[:,:,0] > 120)
        arr[red_mask] = [245, 245, 245]
        # жълт фон
        yellow_mask = (arr[:,:,0] > 180) & (arr[:,:,1] > 140) & (arr[:,:,2] < 100)
        arr[yellow_mask] = [245, 245, 245]
        # зелен фон
        green_mask = (g - r > 40) & (arr[:,:,1] > 100)
        arr[green_mask] = [245, 245, 245]
 
        img_processed = Image.fromarray(arr.astype(np.uint8)).convert("L")
        img_processed = ImageEnhance.Contrast(img_processed).enhance(2.5)
        img_processed = ImageEnhance.Sharpness(img_processed).enhance(3.0)
    else:
        gray = np.array(img_rgb.convert("L"))
        thresh = otsu_threshold(gray)
        binarized = np.where(gray < thresh, 0, 255).astype(np.uint8)
        img_processed = Image.fromarray(binarized)
 
    # уголемяване
    w, h = img_processed.size
    if w < 1600:
        scale = 1600 / w
        interp = Image.NEAREST if img_type == "bw" else Image.LANCZOS
        img_processed = img_processed.resize((int(w * scale), int(h * scale)), interp)
 
    return img_processed, img_type
 
# -------------------------------------------------------------------
# ТЪРСЕНЕ НА Е-ТА
# -------------------------------------------------------------------
def find_e_numbers(text):
    text = text.replace('[', 'E').replace('|', 'E')
    text = text.replace('€', 'E').replace('{', 'E')
    text = text.replace('Е', 'E').replace('е', 'e')  # кирилско -> латинско
 
    pattern = r"e[\s\-_]?\d{3,4}"
    results = re.findall(pattern, text.lower())
 
    cleaned = []
    for r in results:
        r = re.sub(r'[\s\-_]', '', r)
        if r not in cleaned:
            cleaned.append(r)
    return cleaned
 
# -------------------------------------------------------------------
# ЗАРЕЖДАНЕ НА OCR - с кеш за да не се сваля модела всеки път
# -------------------------------------------------------------------
@st.cache_resource(show_spinner="Зарежда се AI моделът... само първия път е бавно ⏳")
def load_reader():
    # пазим модела в /tmp за да оцелее между рестарти
    model_dir = "/tmp/easyocr_models"
    os.makedirs(model_dir, exist_ok=True)
    return easyocr.Reader(
        ['bg', 'en'],
        model_storage_directory=model_dir,
        download_enabled=True
    )
 
# -------------------------------------------------------------------
# ИНТЕРФЕЙС
# -------------------------------------------------------------------
st.title("📷 Проверка за Е-та в храна")
st.caption("Качи снимка на съставките – работи с всякакви етикети")
 
st.info("💡 **Съвет:** Снимай само частта със съставките, на добра светлина.")
 
reader = load_reader()
 
choice = st.radio("Избери начин:", ["📁 Качи снимка", "📷 Камера"])
 
img = None
if choice == "📁 Качи снимка":
    file = st.file_uploader("Качи снимка на етикета", type=["jpg", "jpeg", "png"])
    if file:
        img = Image.open(file)
else:
    cam = st.camera_input("Снимай етикета")
    if cam:
        img = Image.open(cam)
 
if img:
    processed, img_type = preprocess_image(img)
 
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="Оригинал", use_column_width=True)
    with col2:
        caption = "След обработка (черно-бяла)" if img_type == "bw" else "След обработка (цветна)"
        st.image(processed, caption=caption, use_column_width=True)
 
    if st.button("🔍 Провери за Е-та"):
        with st.spinner("Четя текста... малко търпение 🙂"):
            results = reader.readtext(
                np.array(processed),
                detail=1,
                paragraph=False,
                text_threshold=0.5,
                low_text=0.3,
                link_threshold=0.3
            )
            text_parts = [text for (_, text, conf) in results if conf > 0.1]
            text = " ".join(text_parts)
 
        st.subheader("📄 Разчетен текст:")
        if text.strip():
            st.write(text)
        else:
            st.warning("Не успях да прочета текст. Пробвай с по-ясна снимка.")
 
        e_numbers = find_e_numbers(text)
 
        st.subheader(f"⚠️ Намерени Е-та: {len(e_numbers)}")
 
        if e_numbers:
            for e in e_numbers:
                num = e.replace("e", "")
                if not num.isdigit():
                    continue
                category = get_category(num)
                if e in harmful_db:
                    desc, level = harmful_db[e]
                    if level == 3:
                        st.error(f"🔴 **{e.upper()}** – {desc}  \n*{category}*")
                    elif level == 2:
                        st.warning(f"🟡 **{e.upper()}** – {desc}  \n*{category}*")
                    else:
                        st.info(f"🟢 **{e.upper()}** – {desc}  \n*{category}*")
                else:
                    st.info(f"⚪ **{e.upper()}** – {category} (няма специална информация)")
        else:
            st.success("Не намерих Е-та в снимката 👍")
 
        st.divider()
        st.caption("🔴 Много вредно  |  🟡 Внимание  |  🟢 Обикновено безопасно  |  ⚪ Неизвестно")
