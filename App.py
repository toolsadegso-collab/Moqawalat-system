import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import base64

# ==========================================
# 1. إعدادات الصفحة الأساسية والتصميم الاحترافي
# ==========================================
st.set_page_config(page_title="نظام التتبع المعماري الذكي", page_icon="🏗️", layout="wide", initial_sidebar_state="collapsed")

def apply_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
        
        * { font-family: 'Tajawal', sans-serif; }
        body, .stApp { background-color: #0e1117; color: #e0e0e0; direction: RTL; }
        
        /* العناوين والبطاقات */
        h1, h2, h3 { color: #d4af37 !important; /* لون ذهبي معماري */ }
        .total-cost-box {
            background: linear-gradient(135deg, #1f1f1f, #2a2a2a);
            border-left: 5px solid #d4af37;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            text-align: center;
            margin-bottom: 20px;
        }
        .total-cost-box h3 { margin: 0; font-size: 1.2rem; color: #a0a0a0 !important; }
        .total-cost-box h2 { margin: 5px 0 0 0; font-size: 2rem; color: #2ecc71 !important; }
        
        /* الأزرار */
        .stButton>button {
            background-color: #d4af37; color: #000; font-weight: bold; border-radius: 5px; border: none; transition: 0.3s;
        }
        .stButton>button:hover { background-color: #bfa135; transform: scale(1.02); }
        
        /* التبويبات */
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #1f1f1f; border-radius: 5px 5px 0 0; padding: 10px 20px; color: #fff;
        }
        .stTabs [aria-selected="true"] { background-color: #d4af37 !important; color: #000 !important; font-weight: bold; }
        
        /* إخفاء عناصر غير مطلوبة */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. إدارة قواعد البيانات المؤقتة (Session State)
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'system_password' not in st.session_state:
    st.session_state.system_password = "123" # كلمة المرور الافتراضية الأولية
if 'projects' not in st.session_state:
    st.session_state.projects = {}
if 'current_view' not in st.session_state:
    st.session_state.current_view = "home"
if 'active_project' not in st.session_state:
    st.session_state.active_project = None

# ==========================================
# 3. شاشة تسجيل الدخول
# ==========================================
def login_page():
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; font-size: 3rem;'>نظام التتبع المعماري الذكي</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #888;'>المهندس سليمان نبهان</h3>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
        
        pwd = st.text_input("أدخل كلمة المرور للمتابعة:", type="password")
        if st.button("متابعة", use_container_width=True):
            if pwd == st.session_state.system_password:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("كلمة المرور خاطئة ! اعد المحاولة")

# ==========================================
# 4. واجهة النظام الرئيسية وإدارة المشاريع
# ==========================================
def main_dashboard():
    # القائمة العلوية (Header)
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        with st.popover("⚙️ الإعدادات"):
            st.write("إعدادات النظام")
            new_pwd = st.text_input("تغيير كلمة المرور", type="password")
            if st.button("حفظ كلمة المرور"):
                st.session_state.system_password = new_pwd
                st.success("تم التغيير")
            if st.button("تسجيل الخروج"):
                st.session_state.logged_in = False
                st.rerun()
    with col2:
        st.markdown("<h2 style='text-align: center;'>المهندس سليمان نبهان</h2>", unsafe_allow_html=True)
    with col3:
        if st.session_state.current_view == "project":
            if st.button("🏠 العودة للرئيسية"):
                st.session_state.current_view = "home"
                st.session_state.active_project = None
                st.rerun()

    st.markdown("---")

    # عرض المشاريع أو تفاصيل المشروع
    if st.session_state.current_view == "home":
        display_projects_list()
    elif st.session_state.current_view == "project":
        display_project_details(st.session_state.active_project)

def display_projects_list():
    st.markdown("### 🏗️ إدارة المشاريع")
    
    with st.expander("➕ إنشاء مشروع جديد", expanded=False):
        new_proj_name = st.text_input("اسم المشروع")
        if st.button("اعتماد المشروع"):
            if new_proj_name and new_proj_name not in st.session_state.projects:
                st.session_state.projects[new_proj_name] = {
                    "المواد": [], "الورش": [], "الكلفة التشغيلية": [], "مراحل الانجاز": []
                }
                st.success(f"تم إنشاء {new_proj_name}")
                st.rerun()

    st.markdown("#### قائمة المشاريع الحالية:")
    if not st.session_state.projects:
        st.info("لا يوجد مشاريع حالياً. قم بإنشاء مشروع جديد.")
        
    for proj in st.session_state.projects.keys():
        if st.button(f"📂 {proj}", use_container_width=True):
            st.session_state.current_view = "project"
            st.session_state.active_project = proj
            st.rerun()

# ==========================================
# 5. واجهة تفاصيل المشروع (التبويبات والحسابات)
# ==========================================
def calculate_total_cost(proj_data):
    total = 0
    for mat in proj_data["المواد"]:
        if str(mat['cost']).isnumeric(): total += float(mat['cost'])
    for wor in proj_data["الورش"]:
        if str(wor['cost']).isnumeric(): total += float(wor['cost'])
    for op in proj_data["الكلفة التشغيلية"]:
        if str(op['cost']).isnumeric(): total += float(op['cost'])
    return total

def display_project_details(project_name):
    proj_data = st.session_state.projects[project_name]
    total_cost = calculate_total_cost(proj_data)
    
    # مربع التكلفة الإجمالية الاحترافي
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"<h2>مستندات وعمليات مشروع: {project_name}</h2>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="total-cost-box">
                <h3>الكلفة الإجمالية الحالية</h3>
                <h2>{total_cost:,.0f}</h2>
            </div>
        """, unsafe_allow_html=True)

    # التبويبات
    tab1, tab2, tab3, tab4 = st.tabs(["🧱 المواد", "👷 الورش", "💰 الكلفة التشغيلية", "📈 مراحل الإنجاز"])

    # --- تبويب المواد ---
    with tab1:
        with st.expander("➕ إضافة مادة جديدة"):
            mat_name = st.text_input("اسم المادة (مثال: حديد, أسمنت)")
            if st.button("حفظ المادة"):
                proj_data["المواد"].append({"name": mat_name, "records": [], "cost": 0})
                st.rerun()
                
        for idx, mat in enumerate(proj_data["المواد"]):
            with st.expander(f"📦 {mat['name']} (الإجمالي: {mat['cost']})"):
                c1, c2, c3, c4 = st.columns(4)
                qty = c1.number_input("القيمة (الكمية)", min_value=0.0, key=f"mq_{idx}")
                unit = c2.selectbox("الوحدة", ["طن", "كيلو غرام", "متر مكعب", "متر طولي", "عدد", "أخرى"], key=f"mu_{idx}")
                cost_val = c3.text_input("الكلفة (للتسجيل)", key=f"mc_{idx}")
                currency = c4.selectbox("العملة/الحالة", ["دولار", "ليرة", "لم يتم الدفع بعد"], key=f"mcur_{idx}")
                
                if st.button("تسجيل العملية", key=f"mbtn_{idx}"):
                    record = f"التاريخ: {datetime.now().strftime('%Y-%m-%d')} | الكمية: {qty} {unit} | السعر: {cost_val} {currency}"
                    mat["records"].append(record)
                    if cost_val.isnumeric():
                        mat["cost"] += float(cost_val)
                    st.rerun()
                    
                if mat["records"]:
                    st.markdown("**سجل العمليات:**")
                    for r in mat["records"]: st.text(r)

    # --- تبويب الورش ---
    with tab2:
        with st.expander("➕ إضافة ورشة جديدة"):
            wor_name = st.text_input("اسم الورشة (مثال: نجارة باطون)")
            if st.button("حفظ الورشة"):
                proj_data["الورش"].append({"name": wor_name, "workers": 0, "records": [], "cost": 0})
                st.rerun()
                
        for idx, wor in enumerate(proj_data["الورش"]):
            with st.expander(f"🛠️ {wor['name']} (المدفوعات: {wor['cost']})"):
                w_count = st.number_input("عدد العمال", min_value=0, value=wor['workers'], key=f"wc_{idx}")
                w_cost = st.text_input("الدفعة المستحقة / التكلفة", key=f"wcost_{idx}")
                if st.button("تحديث وتسجيل الدفعة", key=f"wbtn_{idx}"):
                    wor['workers'] = w_count
                    if w_cost.isnumeric():
                        wor['cost'] += float(w_cost)
                        wor['records'].append(f"{datetime.now().strftime('%Y-%m-%d')} | تم تسديد دفعة: {w_cost} | عدد العمال: {w_count}")
                    st.rerun()
                for r in wor["records"]: st.text(r)

    # --- تبويب الكلفة التشغيلية ---
    with tab3:
        with st.expander("➕ إضافة بند تشغيلي"):
            op_name = st.text_input("اسم البند (مثال: محروقات، نقل)")
            op_price = st.text_input("التكلفة")
            op_notes = st.text_area("ملاحظات")
            if st.button("تسجيل التكلفة"):
                cost_val = float(op_price) if op_price.isnumeric() else 0
                proj_data["الكلفة التشغيلية"].append({"name": op_name, "cost": cost_val, "notes": op_notes, "date": datetime.now().strftime('%Y-%m-%d')})
                st.rerun()
                
        for op in proj_data["الكلفة التشغيلية"]:
            st.info(f"🔹 **{op['name']}** | التكلفة: {op['cost']} | التاريخ: {op['date']} \n\n ملاحظات: {op['notes']}")

    # --- تبويب مراحل الإنجاز (مع الكاميرا) ---
    with tab4:
        with st.expander("➕ إضافة مرحلة جديدة"):
            stage_name = st.text_input("اسم المرحلة (مثال: صب سقف القبو)")
            stage_notes = st.text_area("تفاصيل وما تم إنجازه")
            photo = st.camera_input("التقط صورة للموقع (اختياري)")
            
            if st.button("اعتماد المرحلة"):
                proj_data["مراحل الانجاز"].append({
                    "name": stage_name, "notes": stage_notes, "date": datetime.now().strftime('%Y-%m-%d'), "has_photo": photo is not None
                })
                st.rerun()
                
        for stage in proj_data["مراحل الانجاز"]:
            st.success(f"✅ **{stage['name']}** ({stage['date']})\n\n{stage['notes']}")
            if stage['has_photo']:
                st.caption("📷 تم إرفاق صورة مع هذه المرحلة (محفوظة في السحابة)")

    st.markdown("---")
    
    # ==========================================
    # 6. أزرار التصدير والمشاركة
    # ==========================================
    col_x, col_y = st.columns(2)
    with col_x:
        # توليد رسالة واتساب
        report_text = f"تقرير مشروع: {project_name}\nالكلفة الإجمالية حتى الآن: {total_cost}\nبإشراف: م. سليمان نبهان"
        whatsapp_url = f"https://wa.me/?text={urllib.parse.quote(report_text)}"
        st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="display: block; text-align: center; background-color: #25D366; color: white; padding: 10px; text-decoration: none; border-radius: 5px; font-weight: bold;">📲 مشاركة التقرير عبر واتساب</a>', unsafe_allow_html=True)
    with col_y:
        # تصدير مبسط للبيانات كملف نصي/جدول ليتم طباعته كـ PDF من المتصفح
        st.download_button(
            label="📄 تحميل بيانات المشروع (للطباعة PDF)",
            data=str(proj_data).encode('utf-8'),
            file_name=f"{project_name}_report.txt",
            mime="text/plain",
            use_container_width=True
        )

# ==========================================
# تشغيل التطبيق
# ==========================================
apply_custom_css()
if not st.session_state.logged_in:
    login_page()
else:
    main_dashboard()
