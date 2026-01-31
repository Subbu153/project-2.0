# Task Summarizer Pro

An improved backend prototype demonstrating CRUD operations, database management, testing, and external API integration using Streamlit and Python.

## Features
1. **Task Management**: Create, Read, Update, Delete tasks with Priority, Status, and Due Date.
2. **AI Summarization**: Mock "AI" summaries generated automatically for task content.
3. **Weather Context**: **(New)** Integration with Open-Meteo API to fetch and log real-time weather data.
4. **Dashboard**: Metrics and charts for task statistics.
5. **HTTP Status Simulation**: Visual feedback mimicking REST API status codes (2xx, 4xx, 5xx).

## Improvements Implemented
- **Testing**: Added a `tests/` suite using Pytest for validation, summarization logic, and DB mocking.
- **Error Handling**: Robust try-except blocks with user-friendly error messages.
- **External API**: Real HTTP requests to Open-Meteo for weather data.

## Setup & Run
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Database Setup**:
   Ensure MySQL is running and `.env` is configured.
   On first run, tables are auto-created.
   To apply schema changes (if upgrading), go to **Settings > Reset Database**.

3. **Run Application**:
   ```bash
   streamlit run app.py
   ```

4. **Run Tests**:
   ```bash
   pytest
   ```

## Why Streamlit?
Streamlit is used here to rapidly prototype the **Backend Logic** (SQLAlchemy, Pydantic, MySQL) without building a complex React/Vue frontend. It allows us to visualize the backend functionality immediately.
