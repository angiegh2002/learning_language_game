import streamlit as st
import requests
from datetime import datetime
import plotly.graph_objects as go

API_URL = "http://localhost:8000"

if 'token' not in st.session_state:
    st.session_state.token = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'page' not in st.session_state:
    st.session_state.page = "login"
if 'admin_page' not in st.session_state:
    st.session_state.admin_page = "لوحة التحكم"
if 'description' not in st.session_state:
    st.session_state.description = ""
if 'generated_description' not in st.session_state:
    st.session_state.generated_description = ""

st.markdown("""
<style>
.block-container {
    max-width: 100% !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}
.main .block-container {
    background-color: #0a1e3f !important;
    color: white;
    min-height: 100vh;
    padding: 1rem 2rem 2rem 2rem;
}
.css-1d391kg {
    background-color: #122a60 !important;
    color: white;
    font-family: 'Cairo', sans-serif;
}
.css-18ni7ap.e8zbici2 {
    color: white !important;
}
* {
    direction: rtl;
    text-align: right;
    font-family: 'Cairo', sans-serif;
}
.stButton>button {
    background-color: #00509e;
    color: white;
    font-size: 16px;
    border-radius: 8px;
    padding: 0.5em 1.2em;
}
.stButton>button:hover {
    background-color: #0077d9;
    color: white;
}
.stTextInput>div>div>input, .stTextArea textarea {
    text-align: right;
    background-color: #f0f4ff !important;
    color: #000000 !important;
    border-radius: 6px;
    padding: 0.3em 0.6em;
    border: 1px solid #a0b0d0;
    font-size: 16px;
    font-family: 'Cairo', sans-serif;
}
.stTextArea textarea::placeholder, .stTextInput>div>div>input::placeholder {
    color: #7a7a7a !important;
}
h1, h2, h3 {
    font-weight: bold;
    color: #00aaff;
    text-shadow: 1px 1px 3px #004080;
}
.stats {
    background-color: #122a60;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
    color: white;
}
button[kind="secondary"] {
    background-color: #cc3300 !important;
    color: white !important;
}
</style>
<link href="https://fonts.googleapis.com/css2?family=Cairo&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

def login():
    st.title("تسجيل الدخول")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("تسجيل الدخول"):
        with st.spinner("جاري التحقق من البيانات..."):
            res = requests.post(f"{API_URL}/admin/login", json={"username": username, "password": password})
        if res.status_code == 200:
            st.session_state.token = res.json()["access_token"]
            st.session_state.is_admin = True
            st.session_state.admin_page = "لوحة التحكم"
            st.rerun()
        else:
            with st.spinner("جاري التحقق من بيانات المستخدم..."):
                res = requests.post(f"{API_URL}/users/login", json={"username": username, "password": password})
            if res.status_code == 200:
                st.session_state.token = res.json()["access_token"]
                st.session_state.is_admin = False
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

    if st.button("إنشاء حساب"):
        st.session_state.page = "register"
        st.rerun()

def register():
    st.title("إنشاء حساب جديد")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("تسجيل"):
        with st.spinner("جاري إنشاء الحساب..."):
            res = requests.post(f"{API_URL}/users/register", json={"username": username, "password": password})
        if res.status_code == 200:
            st.success("تم إنشاء الحساب بنجاح. قم بتسجيل الدخول الآن.")
            st.session_state.page = "login"
        else:
            st.error(res.json().get("detail", "حدث خطأ أثناء إنشاء الحساب"))
    if st.button("عودة إلى تسجيل الدخول"):
        st.session_state.page = "login"
        st.rerun()

def admin_dashboard():
    st.sidebar.title("لوحة التحكم")
    choice = st.sidebar.radio(
        "اختر صفحة:",
        ("لوحة التحكم", "عرض الأسئلة", "إضافة سؤال"),
        index=["لوحة التحكم", "عرض الأسئلة", "إضافة سؤال"].index(st.session_state.admin_page)
    )
    if choice != st.session_state.admin_page:
        st.session_state.admin_page = choice
        st.rerun()

    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    if st.session_state.admin_page == "لوحة التحكم":
        res = requests.get(f"{API_URL}/admin/questions", headers=headers)
        questions = res.json() if res.status_code == 200 else []

        st.markdown("<h1>لوحة التحكم</h1>", unsafe_allow_html=True)
        total_questions = len(questions)
        last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="stats">
                <p> عدد الأسئلة الكلي: <b>{total_questions}</b></p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stats">
                <p> آخر تحديث: <b>{last_update}</b></p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("##  إحصائيات عامة")

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("###  توزيع الأسئلة")
            fig = go.Figure(data=[go.Pie(labels=["أسئلة"], values=[total_questions], hole=0.5)])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', family="Cairo")
            )
            st.plotly_chart(fig, use_container_width=True)

        with col4:
            st.markdown("###  عدد المستخدمين يوميًا")
            res = requests.get(f"{API_URL}/admin/stats/users-per-day", headers=headers)
            if res.status_code == 200:
                data = res.json()
                if data:
                    dates = [item['date'] for item in data]
                    counts = [item['count'] for item in data]
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=dates, y=counts, mode='lines+markers', name='المستخدمين', line_color='#00cc96'))
                    fig.update_layout(
                        xaxis_title='التاريخ',
                        yaxis_title='عدد المستخدمين',
                        paper_bgcolor="#1e1e1e",
                        plot_bgcolor="#1e1e1e",
                        font=dict(color='white', family="Cairo"),
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("لا توجد بيانات.")
            else:
                st.error("فشل في جلب بيانات المستخدمين.")

        col5, col6 = st.columns(2)

        with col5:
            st.markdown("###  عدد الأسئلة يوميًا")
            res = requests.get(f"{API_URL}/admin/stats/questions-per-day", headers=headers)
            if res.status_code == 200:
                data = res.json()
                if data:
                    dates = [item['date'] for item in data]
                    counts = [item['count'] for item in data]
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=dates, y=counts, name='الأسئلة', marker_color='#636EFA'))
                    fig.update_layout(
                        xaxis_title='التاريخ',
                        yaxis_title='عدد الأسئلة',
                        paper_bgcolor="#1e1e1e",
                        plot_bgcolor="#1e1e1e",
                        font=dict(color='white', family="Cairo"),
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("لا توجد بيانات.")
            else:
                st.error("فشل في جلب بيانات الأسئلة.")

        with col6:
            st.markdown("###  الإجابات اليومية")
            res = requests.get(f"{API_URL}/admin/stats/answers-per-day", headers=headers)
            if res.status_code == 200:
                data = res.json()
                if data:
                    dates = [item['date'] for item in data]
                    correct = [item['correct'] for item in data]
                    incorrect = [item['incorrect'] for item in data]
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=dates, y=correct, mode='lines+markers', name="صحيحة", line_color='green'))
                    fig.add_trace(go.Scatter(x=dates, y=incorrect, mode='lines+markers', name="خاطئة", line_color='red'))
                    fig.update_layout(
                        xaxis_title='التاريخ',
                        yaxis_title='عدد الإجابات',
                        paper_bgcolor="#1e1e1e",
                        plot_bgcolor="#1e1e1e",
                        font=dict(color='white', family="Cairo"),
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("لا توجد بيانات.")
            else:
                st.error("فشل في جلب بيانات الإجابات.")

    elif st.session_state.admin_page == "عرض الأسئلة":
        res = requests.get(f"{API_URL}/admin/questions", headers=headers)
        questions = res.json() if res.status_code == 200 else []

        st.header("قائمة الأسئلة")
        if not questions:
            st.info("لا توجد أسئلة لعرضها حالياً.")
        for q in questions:
            st.markdown(f"**الكلمة:** {q['word']}")
            st.markdown(f"**الوصف:** {q['description']}")
            if st.button(f"🗑 حذف السؤال", key=f"delete-{q['id']}"):
                del_res = requests.delete(f"{API_URL}/admin/questions/{q['id']}", headers=headers)
                if del_res.status_code == 200:
                    st.success("تم الحذف")
                    st.rerun()
                else:
                    st.error("حدث خطأ أثناء الحذف")

    elif st.session_state.admin_page == "إضافة سؤال":
        st.header("إضافة سؤال جديد")
        word = st.text_input("الكلمة")
        description = st.text_area("الوصف", value=st.session_state.description)

        col1, col2 = st.columns(2)
        with col1:
            if st.button(" إضافة السؤال"):
                if not word.strip():
                    st.error("يرجى إدخال الكلمة.")
                elif not description.strip():
                    st.error("يرجى إدخال الوصف.")
                else:
                    with st.spinner("جاري الإضافة..."):
                        res = requests.post(
                            f"{API_URL}/admin/questions",
                            json={"word": word.strip(), "description": description.strip()},
                            headers=headers
                        )
                    if res.status_code == 200:
                        st.success("تمت إضافة السؤال")
                        st.session_state.description = ""
                        st.session_state.generated_description = ""
                        st.rerun()
                    else:
                        st.error(res.json().get("detail", "حدث خطأ أثناء الإضافة"))
        with col2:
            if st.button(" توليد وصف تلقائي"):
                if not word.strip():
                    st.error("يرجى إدخال الكلمة أولاً لتوليد الوصف.")
                else:
                    with st.spinner(" جاري توليد الوصف..."):
                        gen = requests.post(
                            f"{API_URL}/admin/questions/generate-description",
                            params={"word": word.strip()},
                            headers=headers
                        )
                    if gen.status_code == 200:
                        st.session_state.generated_description = gen.json().get("generated_description", "")
                        st.rerun()
                    else:
                        st.error("فشل في توليد الوصف")

        if st.session_state.generated_description:
            st.markdown(f"**الوصف المقترح:** {st.session_state.generated_description}")
            if st.button(" استخدام الوصف المقترح"):
                st.session_state.description = st.session_state.generated_description
                st.rerun()
    elif st.session_state.admin_page == "عرض الأسئلة":
        st.header("قائمة الأسئلة")
        if not questions:
            st.info("لا توجد أسئلة لعرضها حالياً.")
        for q in questions:
            st.markdown(f"**الكلمة:** {q['word']}")
            st.markdown(f"**الوصف:** {q['description']}")
            if st.button(f"🗑 حذف السؤال", key=f"delete-{q['id']}"):
                del_res = requests.delete(f"{API_URL}/admin/questions/{q['id']}", headers=headers)
                if del_res.status_code == 200:
                    st.success("تم الحذف")
                    st.rerun()
                else:
                    st.error("حدث خطأ أثناء الحذف")

    else: 
        st.header("إضافة سؤال جديد")
        word = st.text_input("الكلمة")
        description = st.text_area("الوصف", value=st.session_state.description)

        col1, col2 = st.columns(2)
        with col1:
            if st.button(" إضافة السؤال"):
                if not word.strip():
                    st.error("يرجى إدخال الكلمة.")
                elif not description.strip():
                    st.error("يرجى إدخال الوصف.")
                else:
                    with st.spinner("جاري الإضافة..."):
                        res = requests.post(
                            f"{API_URL}/admin/questions",
                            json={"word": word.strip(), "description": description.strip()},
                            headers=headers
                        )
                    if res.status_code == 200:
                        st.success("تمت إضافة السؤال")
                        st.session_state.description = ""
                        st.session_state.generated_description = ""
                        st.rerun()
                    else:
                        st.error(res.json().get("detail", "حدث خطأ أثناء الإضافة"))
        with col2:
            if st.button(" توليد وصف تلقائي"):
                if not word.strip():
                    st.error("يرجى إدخال الكلمة أولاً لتوليد الوصف.")
                else:
                    with st.spinner(" جاري توليد الوصف..."):
                        gen = requests.post(
                            f"{API_URL}/admin/questions/generate-description",
                            params={"word": word.strip()},
                            headers=headers
                        )
                    if gen.status_code == 200:
                        st.session_state.generated_description = gen.json().get("generated_description", "")
                        st.rerun()
                    else:
                        st.error("فشل في توليد الوصف")

        if st.session_state.generated_description:
            st.markdown(f"**الوصف المقترح:** {st.session_state.generated_description}")
            if st.button(" استخدام الوصف المقترح"):
                st.session_state.description = st.session_state.generated_description
                st.rerun()

    # زر تسجيل الخروج
    st.sidebar.markdown("---")
    if st.sidebar.button(" تسجيل الخروج"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.page = "login"
        st.rerun()

def user_interface():
    st.title("مرحبا بك ")
    st.subheader("اختر أحد الأسئلة للإجابة عليه:")

    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    res = requests.get(f"{API_URL}/users/questions", headers=headers)
    if res.status_code == 200:
        for q in res.json():
            with st.expander(f" {q['description']}"):
                answer = st.text_input("اكتب الكلمة الصحيحة:", key=q["id"])
                if st.button(" تحقق", key=f"check-{q['id']}"):
                    with st.spinner("جاري التحقق من إجابتك..."):
                        check = requests.post(
                            f"{API_URL}/users/questions/check-answer",
                            json={"question_id": q["id"], "answer": answer},
                            headers=headers
                        )
                    if check.status_code == 200:
                        if check.json()["correct"]:
                            st.success(" إجابة صحيحة!")
                        else:
                            st.error(" الإجابة خاطئة")

    # زر تسجيل الخروج
    st.sidebar.markdown("---")
    if st.sidebar.button(" تسجيل الخروج"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.page = "login"
        st.rerun()

# --- نقطة تشغيل التطبيق ---
if not st.session_state.token:
    if st.session_state.page == "login":
        login()
    elif st.session_state.page == "register":
        register()
else:
    if st.session_state.is_admin:
        admin_dashboard()
    else:
        user_interface()
