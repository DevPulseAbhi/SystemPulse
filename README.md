# PC Performance Analyzer

A beginner-friendly MCA Semester 1 Python minor project that monitors the
computer running the application. It uses real system data through `psutil`
and presents it in a responsive Streamlit dashboard.

The dashboard always reports the machine where the Streamlit Python process is
running. When run locally, that is your computer. When deployed to Streamlit
Community Cloud or another hosting service, it is the hosted server/container,
not the viewer's computer. A browser-only Streamlit app cannot read a viewer's
CPU, RAM, disk, processes, or network counters without a separate local agent.

## Features

- Live CPU, RAM, disk, and network monitoring
- CPU and RAM history charts
- Network activity chart
- Transparent 0–100 system health score
- Configurable CPU, RAM, and disk threshold alerts
- Running-process table with search and CPU/RAM/name sorting
- System information page
- Performance averages, peaks, minimums, and automatic insights
- CSV monitoring report export
- Bounded in-memory history to avoid unbounded memory growth
- Graceful handling of unavailable permissions and Windows-only metrics
- Network rates are calculated from active non-loopback adapters only
- Windows processor names are read from the friendly hardware model value

## Requirements

- Windows 10 or Windows 11
- Python 3.10 or newer
- Internet access during the one-time package installation

## Windows setup

Open **PowerShell** in the project folder:

```powershell
cd "E:\Python Mini Project"
```

Create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, allow scripts for the current user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Install the project dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run the dashboard

```powershell
python -m streamlit run app.py
```

Open the URL shown by Streamlit, usually:

```text
http://localhost:8501
```

The dashboard refreshes live approximately every two seconds. Keep the
PowerShell window open while demonstrating the application.

## Deployment behavior

After deployment, the application will show a visible **Monitoring host**
label. This prevents hosted server metrics from being mistaken for local
computer metrics. The displayed processor, memory, disk, processes, and
network values are exact readings available to the deployed Python process.

To monitor a particular Windows computer, run the application locally on that
computer. Do not interpret a hosted instance as a remote monitoring solution.

## Project structure

```text
app.py            Streamlit pages, layout, charts, and controls
monitor.py        Real psutil monitoring and Windows-safe data collection
analytics.py      History, statistics, health score, alerts, and insights
requirements.txt  Compatible runtime dependencies
README.md         Setup and troubleshooting guide
```

## Troubleshooting

### A metric says “Unavailable”

Some Windows systems do not expose CPU temperature, disk activity counters, or
specific process information. The application deliberately shows
“Unavailable” instead of incorrectly treating missing data as zero.

### Some processes are missing

Windows may deny access to protected or elevated processes. Run PowerShell as
Administrator only if your demonstration requires additional visibility.
Process termination is intentionally not supported.

### The dashboard does not open

Confirm that the terminal shows a successful Streamlit start message and that
port 8501 is not already in use. A different port can be selected with:

```powershell
python -m streamlit run app.py --server.port 8502
```

Then open `http://localhost:8502`.

### Packages cannot be installed

Verify that the virtual environment is active and check the selected Python:

```powershell
python --version
python -m pip --version
```

Then retry:

```powershell
python -m pip install -r requirements.txt
```

### High RAM alert during a demonstration

The alert uses the actual current computer usage. Close unnecessary programs
or adjust the RAM threshold in the sidebar. No monitoring values are
fabricated.

## Upload to GitHub

From PowerShell in the project folder:

```powershell
git init
git add app.py monitor.py analytics.py requirements.txt README.md features.md uidesign.md .gitignore
git commit -m "Initial PC Performance Analyzer project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPOSITORY` with your GitHub details.
Do not add `.venv`, `.env`, passwords, access tokens, or generated cache files.
