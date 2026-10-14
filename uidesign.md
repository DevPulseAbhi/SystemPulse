

## 🎨 UI Design — PC Performance Analyzer

### Overall style

**Theme:** Dark / modern / technical  
**Layout:** Sidebar + dashboard  
**Colors:** Charcoal background + white text + subtle accent colors  
**Cards:** Rounded, clean, minimal borders  
**Charts:** Simple, not overloaded

Think:

> **Windows Task Manager × modern SaaS dashboard**

---

### 🖥️ Main Dashboard

```text
┌──────────────────────────────────────────────────────────────────┐
│  ◉ PC PERFORMANCE ANALYZER                     ● Monitoring      │
├──────────────┬───────────────────────────────────────────────────┤
│              │                                                   │
│  DASHBOARD   │  Good afternoon 👋                               │
│              │  Your system is running normally.                │
│  📊 Overview │                                                   │
│  📈 Analytics│  ┌────────────┐ ┌────────────┐ ┌────────────┐    │
│  ⚙ Processes│  │    CPU     │ │    RAM     │ │    DISK    │    │
│  💻 System  │  │    34%     │ │    61%     │ │    72%     │    │
│              │  │   Normal   │ │   Normal   │ │    High    │    │
│              │  └────────────┘ └────────────┘ └────────────┘    │
│              │                                                   │
│              │  ┌───────────────────────┐ ┌──────────────────┐ │
│              │  │ CPU PERFORMANCE       │ │ SYSTEM HEALTH    │ │
│              │  │                       │ │                  │ │
│              │  │     ╭──╮              │ │       84         │ │
│              │  │ ╭───╯  ╰──╮           │ │      /100        │ │
│              │  │─╯          ╰──        │ │                  │ │
│              │  │                       │ │  CPU       ✓     │ │
│              │  │  10:01  10:02  10:03 │ │  RAM       ✓     │ │
│              │  └───────────────────────┘ │  Disk      ⚠     │ │
│              │                             └──────────────────┘ │
│              │                                                   │
│              │  ┌─────────────────────────────────────────────┐ │
│              │  │ NETWORK ACTIVITY                            │ │
│              │  │ ↓ 4.2 MB/s       ↑ 1.1 MB/s               │ │
│              │  │                                             │ │
│              │  │     ╭────╮       ╭──╮                      │ │
│              │  │ ────╯    ╰───────╯  ╰────                  │ │
│              │  └─────────────────────────────────────────────┘ │
└──────────────┴───────────────────────────────────────────────────┘
```

---

## 🎨 Color direction

I'd use something like:

```text
Background       #0B0F14
Sidebar          #10151C
Cards            #151B23
Primary text     #F1F5F9
Secondary text   #94A3B8

Accent           Blue/Cyan
Success          Green
Warning          Amber
Critical         Red
```

But keep colors **subtle**. Don't make every card a different neon color. Otherwise it starts looking like a gaming keyboard had a nervous breakdown. 😂

---

## 📊 Analytics Page

This page should be where you demonstrate the **data analytics** aspect.

```text
┌──────────────────────────────────────────────────────────────┐
│ Performance Analytics                         Last 10 Minutes│
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  CPU Usage               RAM Usage                            │
│  ┌──────────────────┐    ┌──────────────────┐                │
│  │     📈           │    │      📈          │                │
│  │                  │    │                  │                │
│  └──────────────────┘    └──────────────────┘                │
│                                                              │
│  Average CPU      42%        Peak CPU       87%              │
│  Average RAM      61%        Peak RAM       79%              │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Network Activity                                       │  │
│  │                    📈                                  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  INSIGHTS                                                   │
│  • CPU usage is stable                                      │
│  • RAM usage is moderate                                    │
│  • Disk usage is relatively high                            │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔍 Processes Page

Make this look like a clean table:

```text
┌─────────────────────────────────────────────────────────────┐
│ Running Processes                                           │
│                                                             │
│ Search process...                                           │
│                                                             │
│ Process              CPU          RAM          Status        │
│ ─────────────────────────────────────────────────────────── │
│ Chrome               18.2%        1.24 GB      Running      │
│ VS Code               8.4%        620 MB       Running      │
│ Python                4.1%        210 MB       Running      │
│ Explorer              2.8%        180 MB       Running      │
│ Spotify               1.4%        140 MB       Running      │
└─────────────────────────────────────────────────────────────┘
```

Allow sorting by **CPU** and **RAM**.

---

## 💻 System Information

Keep this page simple:

```text
SYSTEM INFORMATION

Processor
Intel Core Ultra 5 XXXXX

CPU Cores
14 Cores / 14 Threads

Memory
16 GB

Operating System
Windows 11

Architecture
64-bit

Python
3.13.x

Boot Time
Today, 09:42 AM
```

---

# One UI feature I'd definitely add

### 🟢 Live status indicator

Top-right:

**● Monitoring**

And when data is being refreshed:

**● Live**

If monitoring fails:

**● Connection/Error**

That immediately communicates to the examiner that this isn't just a static dashboard.

---

# The overall design philosophy

Don't try to make it **"fancy."**

Make it:

**Clean → readable → live → professional.**


> **Modern dark desktop monitoring dashboard, sidebar navigation, responsive Streamlit layout, charcoal background, clean rounded metric cards, subtle blue accent, white typography, minimal borders, live status indicator, real-time metric cards, interactive Plotly charts, professional SaaS dashboard aesthetic, no excessive gradients, no excessive animations, no unnecessary icons, no clutter.**