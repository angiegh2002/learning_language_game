import streamlit as st
import requests
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

API_URL = "http://localhost:8000"

st.markdown("""
<style>
/* استدعاء خط جميل */
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');

/* إعدادات عامة */
* {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl;
    text-align: right;
}

body {
    background: #f5f7fa;
}

/* الحاوية الرئيسية */
.main .block-container {
    background-color: #ffffff !important;
    border-radius: 20px;
    padding: 3rem !important;
    box-shadow: 0 15px 40px rgba(0,0,0,0.1);
    margin-top: 2rem !important;
}

/* العناوين */
h1, h2, h3 {
    font-weight: 700 !important;
    color: #2c3e50 !important;
}

h1 {
    font-size: 2.5rem;
    text-align: center;
    margin-bottom: 2rem;
    background: linear-gradient(90deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* الأزرار */
.stButton>button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: #fff !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    border-radius: 25px !important;
    padding: 0.8em 1.5em !important;
    transition: all 0.3s ease;
    box-shadow: 0 6px 20px rgba(0,0,0,0.2);
}

.stButton>button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

/* إدخالات النصوص */
.stTextInput>div>div>input,
.stTextArea textarea {
    border-radius: 12px !important;
    padding: 0.8em 1em !important;
    font-size: 16px;
    border: 2px solid #e9ecef !important;
    background-color: #f8f9fa;
    color: #333;
}

.stTextInput>div>div>input:focus,
.stTextArea textarea:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
}

/* بطاقات الأسئلة */
.question-card {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 6px 20px rgba(0,0,0,0.2);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    cursor: pointer;
}

.question-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

/* لوحة الإحصائيات */
.stats {
    background: #ffffff;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    transition: transform 0.3s ease;
}

.stats:hover {
    transform: translateY(-5px);
}

/* الشريط الجانبي */
.css-1d391kg {
    background: #2c3e50 !important;
    color: white !important;
    border-radius: 15px !important;
    padding: 1rem !important;
}

/* استجابة الموبايل */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1.5rem !important;
        margin: 1rem !important;
    }
    
    h1 {
        font-size: 2rem !important;
    }
    
    .stButton>button {
        width: 100% !important;
    }
}
</style>
""", unsafe_allow_html=True)

defaults = {
    'token': None,
    'is_admin': False,
    'page': "login",
    'admin_page': "لوحة التحكم",
    'description': "",
    'generated_description': "",
    'username': "",
    'answers_status': None,
    'current_question': None
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

class Auth:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def login(self, username: str, password: str):
   
        try:
            res = requests.post(f"{self.api_url}/admin/login", json={"username": username, "password": password})
        except Exception as e:
            return {"error": str(e)}
        if res.status_code == 200:
            return {"token": res.json().get("access_token"), "is_admin": True}

        try:
            res2 = requests.post(f"{self.api_url}/users/login", json={"username": username, "password": password})
        except Exception as e:
            return {"error": str(e)}
        if res2.status_code == 200:
            return {"token": res2.json().get("access_token"), "is_admin": False, "username": username}

        return None

    def register(self, username: str, password: str):
        try:
            res = requests.post(f"{self.api_url}/users/register", json={"username": username, "password": password})
            return res
        except Exception as e:
            return None

class AdminDashboard:
    def __init__(self, api_url: str, token: str):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {token}"}

    def show(self):
        st.sidebar.title("لوحة التحكم")
        choices = ("لوحة التحكم", "عرض الأسئلة", "إضافة سؤال")
        idx = choices.index(st.session_state.admin_page) if st.session_state.admin_page in choices else 0
        choice = st.sidebar.radio("اختر صفحة:", choices, index=idx)
        if choice != st.session_state.admin_page:
            st.session_state.admin_page = choice
            st.rerun()

        if st.session_state.admin_page == "لوحة التحكم":
            self.dashboard()
        elif st.session_state.admin_page == "عرض الأسئلة":
            self.view_questions()
        elif st.session_state.admin_page == "إضافة سؤال":
            self.add_question()

        st.sidebar.markdown("---")
        if st.sidebar.button(" تسجيل الخروج"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.page = "login"
            st.rerun()

    def dashboard(self):
        res = requests.get(f"{self.api_url}/admin/questions", headers=self.headers)
        questions = res.json() if res.status_code == 200 else []

        st.markdown("<h1> لوحة التحكم الإدارية</h1>", unsafe_allow_html=True)

        total_questions = len(questions)
        last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        st.markdown("###  المؤشرات الرئيسية")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea, #00a676);
                color: white;
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 6px 20px rgba(0,0,0,0.15);
                transition: transform 0.3s ease;
            ">
                <h3 style="margin:0; font-weight:600;"> إجمالي الأسئلة</h3>
                <h1 style="margin:10px 0; font-size:2.5rem;">{total_questions}</h1>
                <p style="opacity:0.9; margin:0;">حتى {last_update}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            res_users = requests.get(f"{self.api_url}/admin/stats/users-per-day", headers=self.headers)
            total_users = 0
            if res_users.status_code == 200 and res_users.json():
                total_users = sum(item.get('count', 0) for item in res_users.json())
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #00b894, #00a676);
                color: white;
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 6px 20px rgba(0,0,0,0.15);
                transition: transform 0.3s ease;
            ">
                <h3 style="margin:0; font-weight:600;"> إجمالي المستخدمين</h3>
                <h1 style="margin:10px 0; font-size:2.5rem;">{total_users}</h1>
                <p style="opacity:0.9; margin:0;">مسجلين حتى اليوم</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            res_answers = requests.get(f"{self.api_url}/admin/stats/answers-per-day", headers=self.headers)
            accuracy_rate = 0
            if res_answers.status_code == 200 and res_answers.json():
                data = res_answers.json()
                total_correct = sum(item.get('correct', 0) for item in data)
                total_incorrect = sum(item.get('incorrect', 0) for item in data)
                total_answers = total_correct + total_incorrect
                if total_answers > 0:
                    accuracy_rate = (total_correct / total_answers) * 100
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #fd79a8, #e84393);
                color: white;
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 6px 20px rgba(0,0,0,0.15);
                transition: transform 0.3s ease;
            ">
                <h3 style="margin:0; font-weight:600;"> نسبة الدقة</h3>
                <h1 style="margin:10px 0; font-size:2.5rem;">{accuracy_rate:.1f}%</h1>
                <p style="opacity:0.9; margin:0;">بناءً على الإجابات</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("###  تحليل الأداء")
        col4, col5 = st.columns(2)

        with col4:
            st.markdown("####  توزيع الأسئلة حسب نسبة النجاح")
            res = requests.get(f"{self.api_url}/admin/stats/questions-by-success-rate", headers=self.headers)
            if res.status_code == 200:
                data = res.json()
                if data:
                    labels = [item.get('difficulty_group') for item in data]
                    values = [item.get('question_count') for item in data]
                    colors = ['#00b894', '#fdcb6e', '#e17055', '#6c5ce7']
                    fig = go.Figure(data=[go.Pie(
                        labels=labels,
                        values=values,
                        hole=0.4,
                        textinfo='label+percent',
                        insidetextorientation='radial',
                        marker=dict(colors=colors),
                        hovertemplate="<b>%{label}</b><br>عدد الأسئلة: %{value}<extra></extra>"
                    )])
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#2c3e50', family="Cairo"),
                        showlegend=False,
                        margin=dict(t=0, b=0, l=0, r=0),
                        height=300
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("لا توجد بيانات كافية لتحليل نسبة النجاح.")
            else:
                st.error("فشل في جلب تحليل نسبة نجاح الأسئلة.")

        # عدد المستخدمين يوميًا
        with col5:
            st.markdown("####  عدد المستخدمين يوميًا")
            res = requests.get(f"{self.api_url}/admin/stats/users-per-day", headers=self.headers)
            if res.status_code == 200:
                data = res.json()
                if data:
                    dates = [item.get('date') for item in data]
                    counts = [item.get('count') for item in data]
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=dates,
                        y=counts,
                        mode='lines+markers',
                        name='المستخدمين',
                        line=dict(color='#00b894', width=3),
                        marker=dict(size=8, color='#00b894', line=dict(width=2, color='white'))
                    ))
                    fig.update_layout(
                        xaxis_title='التاريخ',
                        yaxis_title='عدد المستخدمين',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#2c3e50', family="Cairo"),
                        height=300,
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor='#e0e0e0')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("لا توجد بيانات.")
            else:
                st.error("فشل في جلب بيانات المستخدمين.")

        col6, col7 = st.columns(2)

        with col6:
            st.markdown("####  عدد الأسئلة المضافة يوميًا")
            res = requests.get(f"{self.api_url}/admin/stats/questions-per-day", headers=self.headers)
            if res.status_code == 200:
                data = res.json()
                if data:
                    dates = [item.get('date') for item in data]
                    counts = [item.get('count') for item in data]
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=dates,
                        y=counts,
                        name='الأسئلة',
                        marker_color='#74b9ff',
                        marker_line_color='#0984e3',
                        marker_line_width=1.5
                    ))
                    fig.update_layout(
                        xaxis_title='التاريخ',
                        yaxis_title='عدد الأسئلة',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#2c3e50', family="Cairo"),
                        height=300,
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor='#e0e0e0')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("لا توجد بيانات.")
            else:
                st.error("فشل في جلب بيانات الأسئلة.")

        with col7:
            st.markdown("#### الإجابات اليومية (صحيحة vs خاطئة)")
            res = requests.get(f"{self.api_url}/admin/stats/answers-per-day", headers=self.headers)
            if res.status_code == 200:
                data = res.json()
                if data:
                    dates = [item.get('date') for item in data]
                    correct = [item.get('correct') for item in data]
                    incorrect = [item.get('incorrect') for item in data]
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=dates, y=correct,
                        mode='lines+markers',
                        name="صحيحة",
                        line=dict(color='#00b894', width=3),
                        marker=dict(size=7)
                    ))
                    fig.add_trace(go.Scatter(
                        x=dates, y=incorrect,
                        mode='lines+markers',
                        name="خاطئة",
                        line=dict(color='#e17055', width=3),
                        marker=dict(size=7)
                    ))
                    fig.update_layout(
                        xaxis_title='التاريخ',
                        yaxis_title='عدد الإجابات',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#2c3e50', family="Cairo"),
                        height=300,
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor='#e0e0e0'),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("لا توجد بيانات.")
            else:
                st.error("فشل في جلب بيانات الإجابات.")

    def view_questions(self):
        res = requests.get(f"{self.api_url}/admin/questions", headers=self.headers)
        questions = res.json() if res.status_code == 200 else []

        st.header("قائمة الأسئلة")
        if not questions:
            st.info("لا توجد أسئلة لعرضها حالياً.")
            return

        for q in questions:
            st.markdown(f"**الكلمة:** {q.get('word')}")
            st.markdown(f"**الوصف:** {q.get('description')}")
            if st.button(f"🗑 حذف السؤال", key=f"delete-{q.get('id')}"):
                del_res = requests.delete(f"{self.api_url}/admin/questions/{q.get('id')}", headers=self.headers)
                if del_res.status_code == 200:
                    st.success("تم الحذف")
                    st.rerun()
                else:
                    st.error("حدث خطأ أثناء الحذف")

    def add_question(self):
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
                            f"{self.api_url}/admin/questions",
                            json={"word": word.strip(), "description": description.strip()},
                            headers=self.headers
                        )
                    if res.status_code == 200:
                        st.success("تمت إضافة السؤال")
                        st.session_state.description = ""
                        st.session_state.generated_description = ""
                        st.rerun()
                    else:
                        try:
                            st.error(res.json().get("detail", "حدث خطأ أثناء الإضافة"))
                        except:
                            st.error("حدث خطأ أثناء الإضافة")

        with col2:
            if st.button(" توليد وصف تلقائي"):
                if not word.strip():
                    st.error("يرجى إدخال الكلمة أولاً لتوليد الوصف.")
                else:
                    with st.spinner(" جاري توليد الوصف..."):
                        gen = requests.post(
                            f"{self.api_url}/admin/questions/generate-description",
                            params={"word": word.strip()},
                            headers=self.headers
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

class UserInterface:
    def __init__(self, api_url: str, token: str, username: str):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}
        self.username = username

    def show(self):
        st.title(f"مرحبا بك، {self.username} ")

        res = requests.get(f"{self.api_url}/users/questions", headers=self.headers)
        if res.status_code != 200:
            st.error("فشل في جلب الأسئلة")
            return
        questions = res.json()

        if st.session_state.answers_status is None:
            progress_res = requests.get(f"{self.api_url}/users/progress", headers=self.headers)
            if progress_res.status_code == 200:
                logs = progress_res.json()
                st.session_state.answers_status = {q["id"]: None for q in questions}
                for log in logs:
                    st.session_state.answers_status[log["question_id"]] = log["is_correct"]
            else:
                st.session_state.answers_status = {q["id"]: None for q in questions}

        if st.session_state.current_question is None:
            st.subheader("الأسئلة المتاحة:")
            cols = st.columns(3)
            for idx, q in enumerate(questions, start=1):
                col = cols[(idx - 1) % 3]
                with col:
                    status_icon = ""
                    qid = q.get("id")
                    if st.session_state.answers_status.get(qid) is True:
                        status_icon = "✅"
                    elif idx > 1:
                        prev_q = questions[idx - 2]
                        if st.session_state.answers_status.get(prev_q.get("id")) is not True:
                            status_icon = "🔒"

                    clickable = status_icon != "🔒"

                    st.markdown(
                        f"""
                        <div style="
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            border-radius: 15px;
                            padding: 20px;
                            text-align: center;
                            margin: 10px;
                            box-shadow: 0 6px 15px rgba(0,0,0,0.2);
                            cursor: {'pointer' if clickable else 'not-allowed'};
                        ">
                            <h2>السؤال {idx} {status_icon}</h2>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    if clickable and st.button(f"افتح السؤال {idx}", key=f"open-{qid}"):
                        st.session_state.current_question = qid
                        st.rerun()

            st.sidebar.markdown("---")
            if st.sidebar.button(" تسجيل الخروج"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.session_state.page = "login"
                st.rerun()

        else:
            current_q = next((q for q in questions if q.get("id") == st.session_state.current_question), None)
            if not current_q:
                st.error("السؤال غير موجود حالياً")
                st.session_state.current_question = None
                return

            if st.session_state.answers_status.get(current_q.get("id")) is True:
                st.header(f"السؤال: {current_q.get('description')}")
                st.success(" لقد أجبت على هذا السؤال بشكل صحيح. يمكنك مراجعته هنا.")
                st.markdown(f"**الكلمة الصحيحة:** {current_q.get('word')}")
                if st.button(" رجوع لقائمة الأسئلة"):
                    st.session_state.current_question = None
                    st.rerun()
            else:
                st.header(f"السؤال: {current_q.get('description')}")
                answer = st.text_input(" اكتب الكلمة الصحيحة:", key=f"ans-{current_q.get('id')}")

                if st.button("تحقق", key=f"check-{current_q.get('id')}"):
                    with st.spinner("جاري التحقق من إجابتك..."):
                        check = requests.post(
                            f"{self.api_url}/users/questions/check-answer",
                            json={"question_id": current_q.get("id"), "answer": answer},
                            headers=self.headers
                        )
                    if check.status_code == 200:
                        is_correct = check.json().get("correct", False)
                        st.session_state.answers_status[current_q.get("id")] = is_correct

                        try:
                            requests.post(
                                f"{self.api_url}/users/save-progress",
                                json={"question_id": current_q.get("id"), "is_correct": is_correct},
                                headers=self.headers
                            )
                        except:
                            pass

                        if is_correct:
                            st.success("✅ إجابة صحيحة! سيتم الرجوع لقائمة الأسئلة...")
                            st.session_state.current_question = None
                            st.rerun()
                        else:
                            st.error("❌ إجابة خاطئة، حاول مرة أخرى")

                if st.button("⬅️ رجوع لقائمة الأسئلة"):
                    st.session_state.current_question = None
                    st.rerun()

class App:
    def __init__(self):
        self.auth = Auth(API_URL)

    def run(self):
        if not st.session_state.token:
            if st.session_state.page == "login":
                self.login()
            elif st.session_state.page == "register":
                self.register()
        else:
            if st.session_state.is_admin:
                AdminDashboard(API_URL, st.session_state.token).show()
            else:
                UserInterface(API_URL, st.session_state.token, st.session_state.username).show()

    def login(self):
        st.title("تسجيل الدخول")
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        if st.button("تسجيل الدخول"):
            with st.spinner("جاري التحقق من البيانات..."):
                auth_res = self.auth.login(username, password)
            if auth_res is None:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة")
            elif isinstance(auth_res, dict) and auth_res.get("error"):
                st.error(f"حدث خطأ: {auth_res.get('error')}")
            else:
                # النجاح
                st.session_state.token = auth_res.get("token")
                st.session_state.is_admin = auth_res.get("is_admin", False)
                st.session_state.username = auth_res.get("username", username) if not auth_res.get("is_admin") else ""
                st.session_state.admin_page = "لوحة التحكم"
                st.rerun()

        if st.button("إنشاء حساب"):
            st.session_state.page = "register"
            st.rerun()

    def register(self):
        st.title("إنشاء حساب جديد")
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        if st.button("تسجيل"):
            with st.spinner("جاري إنشاء الحساب..."):
                res = self.auth.register(username, password)
            if res is not None and res.status_code == 200:
                st.success("تم إنشاء الحساب بنجاح. قم بتسجيل الدخول الآن.")
                st.session_state.page = "login"
            else:
                try:
                    st.error(res.json().get("detail", "حدث خطأ أثناء إنشاء الحساب"))
                except:
                    st.error("حدث خطأ أثناء إنشاء الحساب")
        if st.button("عودة إلى تسجيل الدخول"):
            st.session_state.page = "login"
            st.rerun()

if __name__ == "__main__":
    App().run()
