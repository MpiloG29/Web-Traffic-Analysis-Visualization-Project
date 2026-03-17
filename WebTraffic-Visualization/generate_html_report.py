"""

generate_html_report.py - Web Traffic HTML Report Generator

"""
 
import pandas as pd

import plotly.express as px

import plotly.graph_objects as go

from plotly.subplots import make_subplots

import jinja2

import os

from datetime import datetime

import argparse
 
def generate_html_report(csv_path, output_path):

    print("=" * 60)

    print("🌐 WEB TRAFFIC HTML REPORT GENERATOR")

    print("=" * 60)

    # Load data

    print("\n📊 Loading data...")

    df = pd.read_csv(csv_path)

    df['date'] = pd.to_datetime(df['date'])

    # Calculate statistics

    total_visits = df['visits'].sum()

    total_unique = df['unique_visitors'].sum()

    avg_bounce = df['bounce_rate'].mean() * 100

    # Create charts

    print("📈 Generating Plotly charts...")

    # Daily trend chart

    daily = df.groupby('date')['visits'].sum().reset_index()

    fig1 = px.line(daily, x='date', y='visits', title='Daily Traffic Trend')

    # Source pie chart

    source_total = df.groupby('source')['visits'].sum().reset_index()

    fig2 = px.pie(source_total, values='visits', names='source', title='Traffic by Source')

    # Save charts as HTML

    charts_html = {

        'daily_trend': fig1.to_html(full_html=False),

        'source_pie': fig2.to_html(full_html=False)

    }

    # Create HTML template

    html_template = f"""
<!DOCTYPE html>
<html>
<head>
<title>Web Traffic Report</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>

            body {{ font-family: Arial; margin: 40px; background: #f5f5f5; }}

            .header {{ background: #2E86AB; color: white; padding: 30px; border-radius: 10px; }}

            .kpi {{ background: white; padding: 20px; margin: 20px 0; border-radius: 10px; }}

            .chart {{ background: white; padding: 20px; margin: 20px 0; border-radius: 10px; }}
</style>
</head>
<body>
<div class="header">
<h1>Web Traffic Analysis Report</h1>
<p>Period: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}</p>
<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
</div>
<div class="kpi">
<h2>Key Metrics</h2>
<p><strong>Total Visits:</strong> {total_visits:,}</p>
<p><strong>Unique Visitors:</strong> {total_unique:,}</p>
<p><strong>Avg Bounce Rate:</strong> {avg_bounce:.1f}%</p>
</div>
<div class="chart">
<h2>Daily Traffic Trend</h2>

            {charts_html['daily_trend']}
</div>
<div class="chart">
<h2>Traffic Sources</h2>

            {charts_html['source_pie']}
</div>
</body>
</html>

    """

    # Save HTML

    print("🖨️ Saving HTML report...")

    with open(output_path, 'w', encoding='utf-8') as f:

        f.write(html_template)

    file_size = os.path.getsize(output_path)

    print(f"\n✅ HTML Report generated successfully!")

    print(f"  📁 Location: {output_path}")

    print(f"  📊 File size: {file_size:,} bytes")
 
if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('--csv', required=True, help='Path to CSV file')

    parser.add_argument('--output', default='WebTraffic_Report.html', help='Output HTML path')

    args = parser.parse_args()

    generate_html_report(args.csv, args.output)
 