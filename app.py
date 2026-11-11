"""MAGED REAL ESTATE CALCULATOR - Streamlit web app (Arabic / RTL)."""

import html
import json

import streamlit as st
import streamlit.components.v1 as components

from calculator import (
    build_message,
    calculate,
    fmt_money,
    fmt_number,
    parse_amount,
)

st.set_page_config(
    page_title="MAGED REAL ESTATE CALCULATOR",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------------------------------
# Styling: dark navy + gold, RTL, responsive
# --------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

:root {
  --navy-900: #0a1128;
  --navy-800: #0f1b3d;
  --navy-700: #16264f;
  --navy-600: #1f3366;
  --gold: #d4af37;
  --gold-light: #f1d57a;
  --text: #eef1f8;
  --muted: #9aa7c7;
}

html, body, .stApp, [class*="css"] {
  font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif !important;
  direction: rtl;
  text-align: right;
}
.stApp {
  background: radial-gradient(1200px 600px at 80% -10%, #1b2d63 0%, transparent 60%),
              linear-gradient(180deg, var(--navy-900) 0%, var(--navy-800) 100%);
  color: var(--text);
}
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1200px; }
[data-testid="stHorizontalBlock"] { direction: rtl; }

/* ---------- Header ---------- */
.hero {
  text-align: center;
  padding: 1.6rem 1rem 1.3rem;
  margin-bottom: 1.4rem;
  border-radius: 22px;
  background: linear-gradient(135deg, var(--navy-700), var(--navy-800));
  border: 1px solid rgba(212,175,55,.35);
  box-shadow: 0 10px 40px rgba(0,0,0,.35);
}
.hero .en {
  direction: ltr;
  font-size: clamp(1.4rem, 4.2vw, 2.4rem);
  font-weight: 800;
  letter-spacing: 2px;
  background: linear-gradient(90deg, var(--gold), var(--gold-light), var(--gold));
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero .ar { color: var(--muted); font-size: clamp(.95rem, 2.4vw, 1.15rem); margin-top: .3rem; }
.hero .bar { width: 90px; height: 3px; margin: .9rem auto 0; border-radius: 3px;
             background: linear-gradient(90deg, transparent, var(--gold), transparent); }

/* ---------- Section titles ---------- */
.section-title {
  font-size: 1.25rem; font-weight: 700; color: var(--gold);
  margin: .2rem 0 .8rem; padding-right: .8rem;
  border-right: 4px solid var(--gold);
}

/* ---------- Inputs ---------- */
.stTextInput label p, .stNumberInput label p {
  color: var(--text) !important; font-size: 1.05rem !important; font-weight: 600 !important;
}
div[data-baseweb="input"], div[data-baseweb="base-input"] {
  background: var(--navy-700) !important;
  border-radius: 14px !important;
  border: 1.5px solid var(--navy-600) !important;
}
div[data-baseweb="input"]:focus-within {
  border-color: var(--gold) !important;
  box-shadow: 0 0 0 3px rgba(212,175,55,.25) !important;
}
div[data-baseweb="input"] input {
  font-size: 1.35rem !important; font-weight: 700 !important;
  height: 3.1rem; color: #fff !important;
  direction: ltr; text-align: right; font-family: 'Cairo', sans-serif !important;
}
.stNumberInput button { background: var(--navy-600) !important; color: var(--gold) !important; }

/* ---------- Buttons ---------- */
.stButton > button {
  width: 100%; height: 3.1rem; border-radius: 14px; font-weight: 700; font-size: 1.05rem;
  background: transparent; color: var(--gold); border: 1.5px solid var(--gold);
  font-family: 'Cairo', sans-serif;
}
.stButton > button:hover { background: var(--gold); color: var(--navy-900); border-color: var(--gold); }

/* ---------- Result cards ---------- */
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; }
.card {
  position: relative; overflow: hidden;
  background: linear-gradient(145deg, var(--navy-700), var(--navy-800));
  border: 1px solid rgba(212,175,55,.25);
  border-radius: 18px; padding: 1.05rem 1.15rem;
  box-shadow: 0 6px 22px rgba(0,0,0,.28);
  transition: transform .18s ease, border-color .18s ease;
}
.card:hover { transform: translateY(-3px); border-color: var(--gold); }
.card::before { content: ""; position: absolute; top: 0; right: 0; width: 5px; height: 100%;
                background: linear-gradient(180deg, var(--gold), var(--gold-light)); }
.card .icon { font-size: 1.5rem; }
.card .label { color: var(--muted); font-size: .98rem; font-weight: 600; margin-top: .2rem; }
.card .value { color: #fff; font-size: 1.55rem; font-weight: 800; margin-top: .25rem; direction: ltr; text-align: right; }
.card .value small { font-size: .85rem; color: var(--gold); font-weight: 700; margin-right: .3rem; }
.card.gold { background: linear-gradient(145deg, #8f7418, var(--gold)); border-color: var(--gold-light); }
.card.gold .label { color: #2a2205; }
.card.gold .value, .card.gold .value small { color: var(--navy-900); }
.card.gold::before { background: var(--navy-900); }

.empty {
  text-align: center; color: var(--muted); padding: 2.5rem 1rem; border-radius: 18px;
  border: 2px dashed var(--navy-600); background: rgba(22,38,79,.4); font-size: 1.1rem;
}
.note { color: var(--muted); font-size: .85rem; margin-top: .8rem; text-align: center; }

/* ---------- Alerts ---------- */
[data-testid="stAlert"] { direction: rtl; border-radius: 12px; }

@media (max-width: 640px) {
  .block-container { padding-left: .8rem; padding-right: .8rem; }
  .card .value { font-size: 1.3rem; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# --------------------------------------------------------------------------
# State
# --------------------------------------------------------------------------
DEFAULTS = {"price_txt": "", "down_pct": 10.0, "years": 5, "discount": 0.0}
for _k, _v in DEFAULTS.items():
    st.session_state.setdefault(_k, _v)


def clear_all() -> None:
    for key, value in DEFAULTS.items():
        st.session_state[key] = value


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def card(icon: str, label: str, value: str, unit: str = "EGP", gold: bool = False) -> str:
    cls = "card gold" if gold else "card"
    unit_html = f"<small>{html.escape(unit)}</small>" if unit else ""
    return (
        f'<div class="{cls}"><div class="icon">{icon}</div>'
        f'<div class="label">{html.escape(label)}</div>'
        f'<div class="value">{html.escape(value)}{unit_html}</div></div>'
    )


def copy_button(message: str) -> None:
    """Copy-to-clipboard button (works inside Streamlit's iframe via fallback)."""
    payload = json.dumps(message, ensure_ascii=False).replace("</", "<\\/")
    components.html(
        f"""
<style>
  body {{ margin:0; background:transparent; }}
  button {{
    width:100%; height:50px; border-radius:14px; border:none; cursor:pointer;
    font-family:'Cairo','Segoe UI',Tahoma,sans-serif; font-size:17px; font-weight:700;
    color:#0a1128; background:linear-gradient(90deg,#d4af37,#f1d57a);
    box-shadow:0 6px 18px rgba(212,175,55,.3);
  }}
  button:hover {{ filter:brightness(1.06); }}
</style>
<button id="b">📋 نسخ النتائج</button>
<script>
  const text = {payload};
  const btn = document.getElementById('b');
  function fallback() {{
    const ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.focus(); ta.select();
    let ok = false;
    try {{ ok = document.execCommand('copy'); }} catch (e) {{}}
    document.body.removeChild(ta);
    return ok;
  }}
  function done(ok) {{
    btn.textContent = ok ? '✅ تم النسخ بنجاح' : '⚠️ تعذّر النسخ - انسخ النص يدويًا';
    setTimeout(() => btn.textContent = '📋 نسخ النتائج', 2200);
  }}
  btn.addEventListener('click', () => {{
    if (navigator.clipboard && window.isSecureContext) {{
      navigator.clipboard.writeText(text).then(() => done(true), () => done(fallback()));
    }} else {{
      done(fallback());
    }}
  }});
</script>
""",
        height=56,
    )


# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
st.markdown(
    """
<div class="hero">
  <div class="en">MAGED REAL ESTATE CALCULATOR</div>
  <div class="ar">حاسبة التقسيط العقاري — احسب المقدم والأقساط فورًا</div>
  <div class="bar"></div>
</div>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Layout: inputs (right) | results (left) — columns flip automatically in RTL
# --------------------------------------------------------------------------
col_inputs, col_results = st.columns([1, 1.5], gap="large")

error = None
result = None

with col_inputs:
    st.markdown('<div class="section-title">بيانات الوحدة</div>', unsafe_allow_html=True)

    st.text_input(
        "سعر الوحدة (جنيه مصري)",
        key="price_txt",
        placeholder="مثال: 5,000,000",
    )
    st.number_input(
        "نسبة المقدم (%)",
        min_value=0.0, max_value=100.0, step=1.0, format="%.2f", key="down_pct",
    )
    st.number_input(
        "عدد سنوات التقسيط",
        min_value=1, max_value=50, step=1, key="years",
    )
    st.number_input(
        "نسبة الخصم (%) — اختياري",
        min_value=0.0, max_value=100.0, step=0.5, format="%.2f", key="discount",
    )

    st.button("🗑️ مسح الكل", on_click=clear_all, use_container_width=True)

    # Parse + validate the price
    price = None
    try:
        price = parse_amount(st.session_state["price_txt"])
    except ValueError as exc:
        error = str(exc)

    if error:
        st.error(error)
    elif price is not None:
        st.caption(f"السعر المُدخل: {fmt_money(price)} جنيه مصري")

    if price is not None and not error:
        try:
            result = calculate(
                price,
                st.session_state["down_pct"],
                st.session_state["years"],
                st.session_state["discount"],
            )
        except ValueError as exc:
            st.error(str(exc))

with col_results:
    st.markdown('<div class="section-title">النتائج</div>', unsafe_allow_html=True)

    if result is None:
        st.markdown(
            '<div class="empty">📊 أدخل سعر الوحدة لتظهر لك النتائج فورًا</div>',
            unsafe_allow_html=True,
        )
    else:
        cards = []
        if result.discount_pct > 0:
            cards.append(card("🏷️", f"قيمة الخصم ({fmt_number(result.discount_pct)}%)",
                              fmt_money(result.discount_amount)))
            cards.append(card("✅", "السعر بعد الخصم", fmt_money(result.price_after_discount)))
        cards += [
            card("💵", f"قيمة المقدم ({fmt_number(result.down_pct)}%)", fmt_money(result.down_payment)),
            card("📉", "المبلغ المتبقي", fmt_money(result.remaining)),
            card("📅", "إجمالي سنوات التقسيط", fmt_number(result.years), unit="سنة"),
            card("🗓️", "القسط السنوي", fmt_money(result.annual), gold=True),
            card("📆", "القسط الربع سنوي", fmt_money(result.quarterly), gold=True),
            card("🧾", "القسط الشهري", fmt_money(result.monthly), gold=True),
        ]
        st.markdown(f'<div class="grid">{"".join(cards)}</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="note">جميع المبالغ بالجنيه المصري (EGP) — '
            'الخصم يُطبَّق على سعر الوحدة قبل حساب المقدم</div>',
            unsafe_allow_html=True,
        )

        st.write("")
        copy_button(build_message(result))
        with st.expander("معاينة الرسالة"):
            st.code(build_message(result), language=None)
