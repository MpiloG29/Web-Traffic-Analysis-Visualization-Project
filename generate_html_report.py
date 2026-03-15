import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import io
import base64
from jinja2 import Template
from datetime import datetime

CSV_PATH    = "WebTraffic 1.csv"
OUTPUT_HTML = "WebTraffic_Report.html"

# LOAD & PREPARE DATA

def load_data(path):
    df = pd.read_csv(path, parse_dates=["date"])
    df.sort_values("date", inplace=True)
    df.reset_index(drop=True, inplace=True)
    df["bounce_pct"] = df["bounce_rate"] * 100
    return df

# SUMMARY STATISTICS

def compute_summary(df):
    daily_totals = df.groupby("date")["visits"].sum()
    return {
        "date_range":         f"{df['date'].min().strftime('%d %b %Y')} – {df['date'].max().strftime('%d %b %Y')}",
        "total_visits":       int(df["visits"].sum()),
        "total_unique":       int(df["unique_visitors"].sum()),
        "avg_bounce":         round(df["bounce_rate"].mean() * 100, 1),
        "busiest_day":        daily_totals.idxmax().strftime("%d %b %Y"),
        "busiest_day_visits": int(daily_totals.max()),
        "top_source":         df.groupby("source")["visits"].sum().idxmax(),
        "lowest_bounce_page": df.groupby("page")["bounce_rate"].mean().idxmin(),
        "generated_at":       datetime.now().strftime("%d %B %Y at %H:%M"),
    }

# CHARTS TO BASE64

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    buf.seek(0)
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

# CHART A: DAILY VISITS TREND

def chart_daily_trend(df):
    daily = df.groupby("date")["visits"].sum().reset_index()

    fig, ax = plt.subplots(figsize=(9, 3.5), facecolor="white")
    ax.plot(daily["date"], daily["visits"],
            color="#D4537E", lw=2.2, marker="o", ms=5)
    ax.fill_between(daily["date"], daily["visits"], alpha=0.25, color="#F4C0D1")

    ax.set_title("Daily Visits Trend  (13 - 19 Oct 2025)", fontsize=11, fontweight="bold", color="#4B1528", pad=10)
    ax.set_ylabel("Total Visits", fontsize=9, color="#99355A")
    ax.tick_params(labelsize=8, colors="#C0A0AA")
    ax.yaxis.grid(True, color="#F4C0D1", linewidth=0.6)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_edgecolor("#C0A0AA")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    fig.tight_layout()
    return fig_to_base64(fig)

# CHART B: VISITS BY SOURCE

def chart_source_bar(df):
    src = (df.groupby("source")["visits"] .sum() .sort_values(ascending=True))

    bar_colours = ["#F4C0D1", "#ED93B1", "#D4537E", "#4B1528"]

    fig, ax = plt.subplots(figsize=(7, 3), facecolor="white")
    bars = ax.barh(src.index, src.values, color=bar_colours[:len(src)], height=0.55)

    for bar in bars:
        w = bar.get_width()
        ax.text(w + 30, bar.get_y() + bar.get_height() / 2, f"{int(w):,}", va="center", fontsize=8, color="#99355A")

    ax.set_title("Total Visits by Traffic Source", fontsize=11, fontweight="bold", color="#4B1528")
    ax.set_xlabel("Visits", fontsize=9, color="#99355A")
    ax.tick_params(labelsize=8, colors="#C0A0AA")
    ax.xaxis.grid(True, color="#F4C0D1", linewidth=0.6)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_edgecolor("#C0A0AA")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig_to_base64(fig)

# CHART C: BOUNCE RATE BY PAGE

def chart_bounce_by_page(df):
    bounce = (df.groupby("page")["bounce_rate"].mean().sort_values(ascending=False)* 100)

    bar_colours = [
        "#72243E" if v > 45 else
        "#D4537E" if v > 38 else
        "#F0997B" if v > 33 else
        "#ED93B1" for v in bounce.values
    ]

    fig, ax = plt.subplots(figsize=(7, 3), facecolor="white")
    bars = ax.bar(bounce.index, bounce.values,
                  color=bar_colours, width=0.55, alpha=0.9)

    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.4,
                f"{h:.1f}%", ha="center", fontsize=8, color="#4B1528")

    ax.set_title("Average Bounce Rate by Page  (%)",
                 fontsize=11, fontweight="bold", color="#4B1528")
    ax.set_ylabel("Bounce Rate (%)", fontsize=9, color="#99355A")
    ax.tick_params(labelsize=8, colors="#C0A0AA")
    ax.yaxis.grid(True, color="#F4C0D1", linewidth=0.6)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_edgecolor("#C0A0AA")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig_to_base64(fig)

# SUMMARY STATS TABLE

def channel_table_rows(df):
    src = (df.groupby("source")
             .agg(
                 visits=("visits", "sum"),
                 unique=("unique_visitors", "sum"),
                 bounce=("bounce_rate", "mean"),
             )
             .reset_index()
             .sort_values("visits", ascending=False))

    src["bounce_pct"] = (src["bounce"] * 100).round(1)

    rows = []
    for _, r in src.iterrows():
        rows.append({
            "source":     r["source"],
            "visits":     f"{int(r['visits']):,}",
            "unique":     f"{int(r['unique']):,}",
            "bounce":     f"{r['bounce_pct']}%",
        })
    return rows

# JINJA2 HTML TEMPLATE

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Web Traffic Analytics Report</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Segoe UI', sans-serif;
    background: "#FBEAF0";
    color: "#4B1528";
    line-height: 1.6;
  }
  .header {
    background: linear-gradient(135deg, "#4B1528", "#99355A");
    color: white;
    padding: 40px 60px;
  }
  .header h1  { font-size: 28px; margin-bottom: 6px; }
  .header .meta { font-size: 13px; opacity: 0.75; }
  .container  { max-width: 1000px; margin: 0 auto; padding: 32px 24px 60px; }
  .section {
    background: white;
    border-radius: 12px;
    padding: 28px;
    margin-bottom: 24px;
    border: 1px solid "#F4C0D1";
  }
  .section h2 {
    font-size: 17px;
    color: "#99355A";
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid "#D4537E";
  }
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 8px;
  }
  .kpi-card {
    background: "#FBEAF0";
    border: 1px solid "#F4C0D1";
    border-radius: 10px;
    padding: 16px;
    text-align: center;
  }
  .kpi-label { font-size: 11px; color: "#C0A0AA"; text-transform: uppercase;
               letter-spacing: 0.8px; margin-bottom: 6px; font-weight: 600; }
  .kpi-value { font-size: 22px; font-weight: 700; color: "#4B1528"; }
  .kpi-sub   { font-size: 11px; color: "#99355A"; margin-top: 4px; }
  .chart-img { width: 100%; border-radius: 8px;
               border: 1px solid "#F4C0D1"; margin-bottom: 6px; }
  .chart-caption { font-size: 12px; color: "#C0A0AA";
                   text-align: center; font-style: italic; }
  .two-col   { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .summary-p { font-size: 14px; color: "#4B1528";
               line-height: 1.8; margin-bottom: 12px; }
  table      { width: 100%; border-collapse: collapse; font-size: 13px; }
  thead tr   { background: "#4B1528"; color: white; }
  thead th   { padding: 10px 14px; text-align: left; font-weight: 600; }
  tbody tr:nth-child(even) { background: "#FBEAF0"; }
  tbody tr:hover           { background: "#F4C0D1"; }
  tbody td   { padding: 9px 14px; border-bottom: 1px solid "#F4C0D1";
               color: "#4B1528"; }
  .footer    { text-align: center; font-size: 12px; color: "#C0A0AA";
               border-top: 1px solid "#F4C0D1" padding-top: 20px; margin-top: 8px; }
  @media(max-width: 650px) {
    .kpi-grid { grid-template-columns: 1fr 1fr; }
    .two-col  { grid-template-columns: 1fr; }
    .header   { padding: 28px 20px; }
  }
</style>
</head>
<body>

<div class="header">
  <h1>Web Traffic Analytics Report</h1>
  <div class="meta">
    Period: {{ stats.date_range }} &nbsp;|&nbsp;
    Generated: {{ stats.generated_at }} &nbsp;|&nbsp;
    Source: WebTraffic 1.csv
  </div>
</div>

<div class="container">

  <!-- KPI CARDS -->
  <div class="section">
    <h2>Key Performance Indicators</h2>
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Total Visits</div>
        <div class="kpi-value">{{ "{:,}".format(stats.total_visits) }}</div>
        <div class="kpi-sub">All pages & sources</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Unique Visitors</div>
        <div class="kpi-value">{{ "{:,}".format(stats.total_unique) }}</div>
        <div class="kpi-sub">Distinct visitors</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Avg Bounce Rate</div>
        <div class="kpi-value">{{ stats.avg_bounce }}%</div>
        <div class="kpi-sub">Across all pages</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Busiest Day</div>
        <div class="kpi-value" style="font-size:16px;">{{ stats.busiest_day }}</div>
        <div class="kpi-sub">{{ "{:,}".format(stats.busiest_day_visits) }} visits</div>
      </div>
    </div>
  </div>

  <!-- EXECUTIVE SUMMARY -->
  <div class="section">
    <h2>Executive Summary</h2>
    <p class="summary-p">
      Over the 7-day period from <strong>{{ stats.date_range }}</strong>, the site recorded
      <strong>{{ "{:,}".format(stats.total_visits) }} total visits</strong> from
      <strong>{{ "{:,}".format(stats.total_unique) }} unique visitors</strong>.
      The average bounce rate was <strong>{{ stats.avg_bounce }}%</strong>.
      The busiest single day was <strong>{{ stats.busiest_day }}</strong>
      with {{ "{:,}".format(stats.busiest_day_visits) }} visits.
      <strong>{{ stats.top_source }}</strong> was the dominant traffic source,
      and the <strong>{{ stats.lowest_bounce_page }}</strong> page had the best visitor retention.
    </p>
  </div>

  <!-- TRAFFIC TREND CHART -->
  <div class="section">
    <h2>Traffic Trends</h2>
    <img class="chart-img" src="{{ chart_daily }}" alt="Daily visits trend"/>
    <p class="chart-caption">Figure 1 — Total daily visits across the reporting period</p>
  </div>

  <!-- SOURCE & BOUNCE CHARTS -->
  <div class="section">
    <h2>Acquisition & Engagement Analysis</h2>
    <div class="two-col">
      <div>
        <img class="chart-img" src="{{ chart_source }}" alt="Visits by source"/>
        <p class="chart-caption">Figure 2 — Visits by traffic source</p>
      </div>
      <div>
        <img class="chart-img" src="{{ chart_bounce }}" alt="Bounce rate by page"/>
        <p class="chart-caption">Figure 3 — Average bounce rate by page</p>
      </div>
    </div>
  </div>

  <!-- CHANNEL TABLE -->
  <div class="section">
    <h2>Channel Breakdown</h2>
    <table>
      <thead>
        <tr>
          <th>Source</th>
          <th>Total Visits</th>
          <th>Unique Visitors</th>
          <th>Avg Bounce Rate</th>
        </tr>
      </thead>
      <tbody>
        {% for row in channel_rows %}
        <tr>
          <td><strong>{{ row.source }}</strong></td>
          <td>{{ row.visits }}</td>
          <td>{{ row.unique }}</td>
          <td>{{ row.bounce }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

  <div class="footer">
    Auto-generated from WebTraffic 1.csv &mdash;
    Automated Reporting Pipeline &mdash;
    {{ stats.generated_at }}
  </div>

</div>
</body>
</html>"""

# BUILD & GENERATE HTML

def build_html(df, stats, output_path):
    print("  Rendering charts...")
    context = {
        # - Data
        "stats":        stats,
        "channel_rows": channel_table_rows(df),
        # - Charts
        "chart_daily":  chart_daily_trend(df),
        "chart_source": chart_source_bar(df),
        "chart_bounce": chart_bounce_by_page(df),
    }

    template = Template(HTML_TEMPLATE)
    html     = template.render(**context)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = len(html.encode("utf-8")) / 1024
    print(f"HTML report saved → {output_path}  ({size_kb:,.0f} KB)")

# RUN & TEST 

if __name__ == "__main__":
    print("Loading data...")
    df    = load_data(CSV_PATH)
    stats = compute_summary(df)
    print(f"    {len(df)} rows | {stats['date_range']}")
    print("Building HTML report...")
    build_html(df, stats, OUTPUT_HTML)