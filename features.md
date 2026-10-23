

## SystemPulse - PC Health analyzer — Feature List

### 1. 🖥️ Live System Dashboard
The main screen should immediately show:

- CPU usage (%)
- RAM usage (%)
- RAM used / total
- Disk usage (%)
- Disk used / total
- Network upload speed
- Network download speed
- System uptime
- Operating system
- Processor name

**Auto-refresh:** every 1–2 seconds.

---

### 2. ⚡ CPU Monitoring
Show:

- Current CPU utilization
- CPU core count
- CPU frequency
- Per-core CPU usage
- CPU usage history graph

Optional:
- CPU temperature **if supported by the system**

---

### 3. 🧠 RAM Monitoring
Show:

- Total RAM
- Used RAM
- Available RAM
- RAM utilization %
- RAM usage history

Example:

```text
RAM
██████████████░░░░  72%

11.5 GB / 16 GB
```

---

### 4. 💾 Disk Monitoring
Show:

- Total storage
- Used storage
- Free storage
- Disk utilization %
- Disk read speed
- Disk write speed

You can show individual drives too:

```text
C:  72% used
D:  41% used
```

---

### 5. 🌐 Network Monitoring
Show:

- Download speed
- Upload speed
- Total data sent
- Total data received
- Network interface name
- Connection status

And a small live network graph.

---

### 6. 📊 Performance Analytics

This is the part that makes it more than a simple monitoring app.

Maintain recent readings and calculate:

- Average CPU usage
- Maximum CPU usage
- Minimum CPU usage
- Average RAM usage
- Maximum RAM usage
- Average network speed
- Peak network speed

Example:

```text
PERFORMANCE SUMMARY

Average CPU       38%
Peak CPU          87%
Average RAM       64%
Peak RAM          79%
Peak Download     8.4 MB/s
```

---

### 7. 📈 Historical Graphs

Include graphs for:

- CPU usage vs time
- RAM usage vs time
- Network usage vs time
- Disk activity vs time

Have a small time window such as:

**Last 1 min | 5 min | 10 min**

Don't store unlimited data. That's unnecessary.

---

### 8. 🩺 System Health Score

Create a simple score from 0–100 based on resource utilization.

Example:

```text
SYSTEM HEALTH

       84 / 100

CPU       ✓ Normal
RAM       ✓ Normal
Disk      ⚠ High
Network   ✓ Normal
```

Use simple threshold-based logic rather than ML.

---

### 9. 🚨 Performance Alerts

Automatically detect abnormal usage.

For example:

```text
⚠ HIGH CPU USAGE

CPU usage has exceeded 85%.

Current: 93%
```

Possible alerts:

- CPU > 85%
- RAM > 85%
- Disk > 90%
- Network spike
- Low disk space

---

### 10. 🔍 Process Monitor

Show the currently running processes.

Something like:

| Process | CPU | RAM |
|---|---:|---:|
| Chrome | 18% | 1.2 GB |
| VS Code | 8% | 620 MB |
| Python | 4% | 210 MB |

Add:

- Search process
- Sort by CPU
- Sort by RAM

**Don't add "kill process" initially.** It's unnecessary and introduces avoidable problems.

---

### 11. 💡 Automatic Performance Insights

Generate simple human-readable observations:

```text
INSIGHTS

• CPU usage is currently normal.
• RAM usage is moderately high.
• Disk usage is above 70%.
• Chrome is currently the highest RAM-consuming process.
• Overall system health is good.
```

This is a very nice little feature for the demo.

---

### 12. 🖥️ System Information Page

Show static hardware/software information:

- Processor
- CPU cores
- RAM
- Operating system
- Computer name
- Python version
- Boot time
- Architecture

Basically a mini **"About this PC"** page.

---

### 13. 📥 Export Performance Report

Keep this simple.

Button:

> **Generate Report**

Generate a CSV containing collected metrics:

```text
Timestamp,CPU,RAM,Disk,Download,Upload
14:05:01,34,61,72,2.4,0.8
14:05:02,37,62,72,3.1,0.7
...
```

This gives you another legitimate **data analytics/data handling** component.

---

# 🎯 What I would actually implement

Since you have **5 other projects**, I'd divide the features into two levels.

### MUST HAVE

- ✅ Live CPU monitoring
- ✅ Live RAM monitoring
- ✅ Live disk monitoring
- ✅ Live network monitoring
- ✅ Performance graphs
- ✅ Basic analytics/statistics
- ✅ System health score
- ✅ Alerts
- ✅ Process monitor
- ✅ System information

### NICE TO HAVE

- 🟡 CPU temperature
- 🟡 Historical data export
- 🟡 Automatic insights
- 🟡 Multiple-drive monitoring
- 🟡 1/5/10-minute filters

### ❌ Don't add

- ❌ Machine learning
- ❌ User authentication
- ❌ Cloud database
- ❌ Docker
- ❌ Login/signup
- ❌ APIs
- ❌ Kubernetes
- ❌ Complex database architecture
- ❌ Remote server monitoring
- ❌ Process termination

Those are **scope creep** for a 1st-sem minor project.

---

## Final project scope

I'd make the application have just **4 pages**:

```text
┌─────────────────────────────┐
│ PC PERFORMANCE ANALYZER     │
├─────────────────────────────┤
│                             │
│ 🏠 Dashboard                │
│ 📊 Analytics                │
│ 🔍 Processes                │
│ ℹ️ System Information       │
│                             │
└─────────────────────────────┘
```

**Dashboard** → live monitoring  
**Analytics** → graphs + statistics + health score  
**Processes** → resource-hungry applications  
**System Info** → hardware/software details