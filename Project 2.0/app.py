import streamlit as st
from streamlit_option_menu import option_menu
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db, init_db, engine
from models import Task, WeatherLog
from schemas import TaskCreate, TaskUpdate
from summarizer import summarize_text
from weather_service import get_weather, log_weather, delete_weather_log
from pydantic import ValidationError
from datetime import date
import pandas as pd
import requests
import altair as alt

# Page Config
st.set_page_config(page_title="Task Summarizer Pro", layout="wide", page_icon="✨")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e6e6ea;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---

def get_session():
    return next(get_db())

def display_status(code: int, message: str):
    """Simulates HTTP Status Codes in the UI."""
    if 200 <= code < 300:
        st.success(f"**{code}**: {message}")
    elif 400 <= code < 500:
        st.warning(f"**{code}**: {message}")
    elif 500 <= code < 600:
        st.error(f"**{code} Internal Server Error**: {message}")
    else:
        st.info(f"**{code}**: {message}")

# --- DB OPERATIONS ---

def create_task(db: Session, title: str, content: str, priority: str, status: str, due_date: date):
    try:
        task_data = TaskCreate(
            title=title, content=content, priority=priority,
            status=status, due_date=due_date
        )
        summary = summarize_text(task_data.content)
        db_task = Task(
            title=task_data.title, content=task_data.content, summary=summary,
            priority=task_data.priority, status=task_data.status, due_date=task_data.due_date
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task, None
    except ValidationError as e:
        return None, (422, f"Validation Error: {e}")
    except Exception as e:
        return None, (500, f"Database Error: {str(e)}")

def delete_task(db: Session, task_id: int):
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task: return False, (404, "Task not found")
        db.delete(task)
        db.commit()
        return True, (200, "Task deleted")
    except Exception as e:
        return False, (500, f"Database Error: {str(e)}")

# --- UI VIEWS ---

def dashboard_view(db: Session):
    st.title("📊 Executive Dashboard")
    
    try:
        # Fetch Data
        df = pd.read_sql(db.query(Task).statement, db.bind)
        
        # Metrics Row
        total = len(df)
        completed = len(df[df['status'] == 'Done']) if not df.empty else 0
        pending = total - completed
        high = len(df[(df['priority'] == 'High') & (df['status'] != 'Done')]) if not df.empty else 0
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Tasks", total, "All time")
        c2.metric("Pending", pending, "Needs Action", delta_color="inverse")
        c3.metric("Completed", completed, "Done")
        c4.metric("High Priority", high, "Critical", delta_color="inverse")
        
        st.divider()
        
        # Charts Row
        col_charts_1, col_charts_2 = st.columns(2)
        
        with col_charts_1:
            st.subheader("Task Status Distribution")
            if not df.empty:
                status_chart = alt.Chart(df).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field="status", type="nominal", aggregate="count"),
                    color=alt.Color(field="status", type="nominal"),
                    tooltip=["status", "count()"]
                ).properties(height=300)
                st.altair_chart(status_chart, use_container_width=True)
            else:
                st.info("No data available.")

        with col_charts_2:
            st.subheader("Priority Breakdown")
            if not df.empty:
                priority_chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X("priority", sort=["Low", "Medium", "High"]),
                    y="count()",
                    color="priority",
                    tooltip=["priority", "count()"]
                ).properties(height=300)
                st.altair_chart(priority_chart, use_container_width=True)
            else:
                st.info("No data available.")

        st.divider()
        st.subheader("Recent Activity Log")
        if not df.empty:
            recent_df = df.sort_values(by="created_at", ascending=False).head(5)
            # Display as a clean table
            st.dataframe(
                recent_df[["title", "status", "priority", "created_at"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.caption("No recent activity.")
            
    except Exception as e:
        display_status(500, f"Dashboard Error: {e}")

def create_task_view(db: Session):
    st.title("➕ Create New Task")
    with st.container():
        st.markdown("Fill in the details below to generate a smart task with AI summary.")
        with st.form("create_task_form", clear_on_submit=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                title = st.text_input("Task Title", placeholder="e.g. Q4 Financial Report")
            with col2:
                priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=1)
                
            content = st.text_area("Task Content", height=150, placeholder="Describe the task details...")
            
            c1, c2 = st.columns(2)
            with c1:
                status = st.selectbox("Status", ["Todo", "In Progress", "Done"])
            with c2:
                due_date = st.date_input("Due Date", value=date.today())
                
            submitted = st.form_submit_button("Create Task", use_container_width=True)
            
            if submitted:
                if not title or not content:
                    display_status(422, "Title and Content are required.")
                else:
                    task, error = create_task(db, title, content, priority, status, due_date)
                    if task:
                        display_status(201, "Task Created successfully.")
                        st.info(f"**AI Summary:** {task.summary}")
                    elif error:
                        display_status(error[0], error[1])

def view_tasks_view(db: Session):
    st.title("📋 Process Management (Table View)")
    
    # Sidebar Filters
    with st.sidebar:
        st.header("🔍 Filter Data")
        status_filter = st.multiselect("Status", ["Todo", "In Progress", "Done"], default=["Todo", "In Progress"])
        priority_filter = st.multiselect("Priority", ["Low", "Medium", "High"])
        search = st.text_input("Search Title")
    
    try:
        # Build Query
        query = db.query(Task)
        if status_filter: query = query.filter(Task.status.in_(status_filter))
        if priority_filter: query = query.filter(Task.priority.in_(priority_filter))
        if search: query = query.filter(Task.title.contains(search))
        
        tasks = query.all()
        
        if not tasks:
            st.info("No matching records found.")
            return

        # Header
        c1, c2, c3, c4, c5, c6 = st.columns([0.5, 2, 1, 1, 1, 0.5])
        c1.markdown("**ID**")
        c2.markdown("**Title**")
        c3.markdown("**Status**")
        c4.markdown("**Priority**")
        c5.markdown("**Due Date**")
        c6.markdown("**Action**")
        
        st.divider()

        # Rows
        for task in tasks:
            c1, c2, c3, c4, c5, c6 = st.columns([0.5, 2, 1, 1, 1, 0.5])
            c1.write(task.id)
            c2.write(task.title)
            
            # Status Badge Logic (Simple Text Color)
            if task.status == "Done":
                c3.success(task.status)
            elif task.status == "In Progress":
                c3.warning(task.status)
            else:
                c3.info(task.status)
                
            c4.write(task.priority)
            c5.write(task.due_date)
            
            # Delete Button
            if c6.button("🗑️", key=f"btn_del_{task.id}", help="Delete Task"):
                success, error = delete_task(db, task.id)
                if success:
                    st.toast(f"Task {task.id} deleted successfully!")
                    st.experimental_rerun()
                else:
                    st.error(error[1])
            
            st.divider() # Separator between rows
        
    except Exception as e:
        display_status(500, f"Error fetching data: {e}")

def weather_view(db: Session):
    st.title("🌦 Global Weather Context")
    
    col_input, col_display = st.columns([1, 2])
    
    with col_input:
        with st.form("weather_form"):
            city = st.text_input("City Name", placeholder="London")
            
            # Advanced Options
            with st.expander("Advanced: API Settings"):
                api_key = st.text_input("OpenWeatherMap API Key", type="password", help="Leave empty to use Open-Meteo (Free)")
                
            submit = st.form_submit_button("Fetch Weather")
    
    if submit and city:
        with st.spinner("Connecting to Satellite..."):
            try:
                # Pass optional API Key
                data = get_weather(city, api_key)
                
                log_weather(db, city, data['temperature'], data['condition'])
                
                with col_display:
                    st.success(f"Weather in **{city}**")
                    st.caption(f"Source: {data.get('source', 'Unknown')}")
                    
                    m1, m2 = st.columns(2)
                    m1.metric("Temperature", data['temperature'])
                    m2.metric("Condition", data['condition'])
            except Exception as e:
                st.error(str(e))

    st.markdown("### Search History")
    
    # Fetch logs
    logs = db.query(WeatherLog).order_by(WeatherLog.timestamp.desc()).limit(10).all()
    
    if not logs:
        st.info("No search history available.")
        return

    # Table Header
    c1, c2, c3, c4, c5 = st.columns([0.5, 1.5, 1, 1.5, 0.5])
    c1.markdown("**ID**")
    c2.markdown("**City**")
    c3.markdown("**Temp**")
    c4.markdown("**Condition**")
    c5.markdown("**Del**")
    st.divider()
    
    # Table Rows
    for log in logs:
        c1, c2, c3, c4, c5 = st.columns([0.5, 1.5, 1, 1.5, 0.5])
        c1.write(log.id)
        c2.write(log.city)
        c3.write(log.temperature)
        c4.write(log.condition)
        
        if c5.button("🗑️", key=f"del_weather_{log.id}"):
            success, error = delete_weather_log(db, log.id)
            if success:
                st.toast(f"Log {log.id} deleted.")
                st.experimental_rerun()
            else:
                st.error(error)
        st.divider()

def manage_tasks_view(db: Session):
    st.title("🛠 Operations")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Delete Record")
        task_id = st.number_input("Enter Task ID to Delete", min_value=1, step=1)
        if st.button("Delete Task", type="primary"):
            success, error = delete_task(db, task_id)
            if success:
                st.success(f"Task {task_id} deleted.")
            else:
                display_status(error[0], error[1])

    with col2:
        st.subheader("System")
        if st.button("Reset Database (Hard Reset)"):
            try:
                from reset_db import reset_database
                reset_database()
                st.balloons()
                st.success("Database Reset Successfully.")
            except Exception as e:
                st.error(f"Reset Failed: {e}")

# Main App Loop
def main():
    try:
        db = get_session()
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return

    # Premium Sidebar Navigation
    with st.sidebar:
        selected = option_menu(
            menu_title="Task Pro",
            options=["Dashboard", "Create Task", "Process View", "Weather", "Manage"],
            icons=["kanban", "plus-circle", "table", "cloud-lightning", "gear"],
            menu_icon="cast",
            default_index=0,
            styles={
                "nav-link-selected": {"background-color": "#ff4b4b"},
            }
        )

    if selected == "Dashboard":
        dashboard_view(db)
    elif selected == "Create Task":
        create_task_view(db)
    elif selected == "Process View":
        view_tasks_view(db)
    elif selected == "Weather":
        weather_view(db)
    elif selected == "Manage":
        manage_tasks_view(db)

if __name__ == "__main__":
    main()
