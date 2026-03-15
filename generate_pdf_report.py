import pandas as pd
import matplotlib
matplotlib.use("Agg")               # Used to prevent a display window from opening
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

CSV_PATH = "WebTraffic 1.csv"
OUTPUT_PDF = "WebTraffic_Report.pdf"

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

# CHARTS TO IMAGE

def fig_to_image(fig, width_cm=16):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return Image(buf, width=width_cm * cm)

# CHART A: DAILY VISITS TREND

def chart_daily_trend(df):
    daily = df.groupby("date")["visits"].sum().reset_index()

    fig, ax = plt.subplots(figsize=(9, 3.5), facecolor="white")
    ax.plot(daily["date"], daily["visits"], color="#D4537E", lw=2.2, marker="o", ms=5)
    ax.fill_between(daily["date"], daily["visits"], alpha=0.12, color="#F4C0D1")

    ax.set_title("Daily Visits Trend (13 - 19 Oct 2025)", fontsize=11, fontweight="bold", color="#4B1528", pad=10)
    ax.set_ylabel("Total Visits", fontsize=9, color="#99355A")
    ax.tick_params(labelsize=8, color="#C0A0AA")
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig_to_image(fig)

# CHART B: VISITS BY SOURCE

def chart_source_bar(df):
    src = (df.groupby("source")["visits"].sum().sort_values(ascending=True))

    fig, ax = plt.subplots(figsize=(7, 3), facecolor="white")
    colors_list = ["#90A4AE", "#F4C0D1", "#7B1FA2", "#ED93B1"]
    bars = ax.barh(src.index, src.values, color=colors_list[:len(src)], height=0.55)

    for bar in bars:
        w = bar.get_width()
        ax.text(w + 30, bar.get_y() + bar.get_height() / 2, f"{int(w):,}", va="center", fontsize=8)

    ax.set_title("Total Visits by Traffic Source", fontsize=11, fontweight="bold")
    ax.set_xlabel("Visits", fontsize=9)
    ax.tick_params(labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig_to_image(fig, width_cm=13)

# CHART C: BOUNCE RATE BY PAGE

def chart_bounce_by_page(df):
    bounce = (df.groupby("page")["bounce_rate"].mean().sort_values(ascending=False)* 100)       # Converts value to percentage

    fig, ax = plt.subplots(figsize=(7, 3), facecolor="white")
    bar_colors = ["#E53935" if v > 40 else "#FF9800" if v > 35 else "#4CAF50"
                  for v in bounce.values]
    bars = ax.bar(bounce.index, bounce.values, color=bar_colors, width=0.55, alpha=0.88)

    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.5, f"{h:.1f}%", ha="center", fontsize=8)

    ax.set_title("Average Bounce Rate by Page  (%)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Bounce Rate (%)", fontsize=9)
    ax.tick_params(labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig_to_image(fig, width_cm=13)

# SUMMARY STATS TABLE

def stats_table(stats):
    data = [
        ["Metric", "Value"],
        ["Report period",         stats["date_range"]],
        ["Total visits",          f"{stats['total_visits']:,}"],
        ["Total unique visitors", f"{stats['total_unique']:,}"],
        ["Avg bounce rate",       f"{stats['avg_bounce']}%"],
        ["Busiest day",           f"{stats['busiest_day']}  ({stats['busiest_day_visits']:,} visits)"],
        ["Top traffic source",    stats["top_source"]],
        ["Best-retaining page",   stats["lowest_bounce_page"]],
    ]

    tbl = Table(data, colWidths=[6 * cm, 10 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#4B1528")),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white,
                                              colors.HexColor("#FBEAF0")]),
        ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#C0A0AA")),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, colors.HexColor("#F4C0D1")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
    ]))
    return tbl

# ASSEMBLE & BUILD PDF

def build_pdf(df, stats, output_path):
    styles = getSampleStyleSheet()

    # - Customize Text Styles
    title_style = ParagraphStyle(
        "title", parent=styles["Title"], fontSize=20, textColor=colors.HexColor("#4B1528"), alignment=TA_CENTER, spaceAfter=6
    )
    body_style = ParagraphStyle(
        "body", parent=styles["Normal"], fontSize=9, leading=14, spaceAfter=4
    )
    heading_style = ParagraphStyle(
        "heading", parent=styles["Heading2"], fontSize=13, textColor=colors.HexColor("#99355A"), spaceBefore=14, spaceAfter=4
    )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title="Web Traffic Analytics Report",
        author="Member 3"
    )

    story = []
    W = A4[0] - 4 * cm

    # - Title & Metadata
    story.append(Paragraph("Web Traffic Analytics Report", title_style))
    story.append(Paragraph(
        f"Period: {stats['date_range']}  |  Generated: {stats['generated_at']}",
        ParagraphStyle("meta", fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor("#90A4AE"))
    ))
    story.append(Spacer(1, 0.4 * cm))
    story.append(HRFlowable(width=W, thickness=2, color=colors.HexColor("#D4537E")))
    story.append(Spacer(1, 0.4 * cm))

    # - Executive Summary Paragraph
    story.append(Paragraph("Executive Summary", heading_style))
    summary_text = (
        f"Over the 7-day period from {stats['date_range']}, the site recorded "
        f"<b>{stats['total_visits']:,} total visits</b> from "
        f"<b>{stats['total_unique']:,} unique visitors</b>. "
        f"The average bounce rate was <b>{stats['avg_bounce']}%</b>. "
        f"The busiest single day was <b>{stats['busiest_day']}</b> "
        f"with {stats['busiest_day_visits']:,} visits. "
        f"<b>{stats['top_source']}</b> was the dominant traffic source, "
        f"and the <b>{stats['lowest_bounce_page']}</b> page had the best visitor retention."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 0.4 * cm))

    # - KPI Table
    story.append(Paragraph("Key Metrics", heading_style))
    story.append(stats_table(stats))
    story.append(Spacer(1, 0.5 * cm))

    # - Chart A
    story.append(Paragraph("Traffic Trends", heading_style))
    story.append(Paragraph(
        "The chart below shows total daily visits across the reporting period.",
        body_style
    ))
    story.append(Spacer(1, 0.2 * cm))
    story.append(chart_daily_trend(df))

    story.append(PageBreak())

    # - Charts B & C (side by side)
    story.append(Paragraph("Acquisition & Engagement Analysis", heading_style))
    story.append(Paragraph(
        "Search is the dominant traffic source. Social media traffic shows the "
        "highest bounce rate, while Contact and Admissions pages retain visitors best.",
        body_style
    ))
    story.append(Spacer(1, 0.3 * cm))

    # - Charts B and C are in a two-column table tto ensure that they are side by side
    side_by_side = Table(
        [[chart_source_bar(df), chart_bounce_by_page(df)]],
        colWidths=[W * 0.50, W * 0.48]
    )
    side_by_side.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(side_by_side)

    # - Footer 
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width=W, thickness=1, color=colors.HexColor("#D4537E")))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        f"Auto-generated from WebTraffic.csv on {stats['generated_at']} — Member 3",
        ParagraphStyle("footer", fontSize=7, alignment=TA_CENTER, textColor=colors.HexColor("#D4537E"))
    ))

    doc.build(story)
    print(f"PDF saved → {output_path}")

# RUN TEST
if __name__ == "__main__":
    print("Loading data...")
    df    = load_data(CSV_PATH)
    stats = compute_summary(df)
    print(f"    {len(df)} rows | {stats['date_range']}")
    print("Building PDF...")
    build_pdf(df, stats, OUTPUT_PDF)