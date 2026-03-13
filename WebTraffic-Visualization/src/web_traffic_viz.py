"""
WebTraffic Visualization Script
Member 2 Tasks: matplotlib, seaborn, plotly visualizations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import os

warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Create directory for saving plots
os.makedirs('visualizations', exist_ok=True)
print("📁 Created/Verified visualizations folder")

# Read the data - try multiple possible locations
print("\n🔍 Looking for CSV file...")

possible_paths = [
    'data/WebTraffic 1.csv',           # In data folder
    'WebTraffic 1.csv',                 # In current directory
    './data/WebTraffic 1.csv',          # Explicit path
    '../data/WebTraffic 1.csv',         # Parent/data folder
    'WebTraffic 1 (1).csv',              # Original name
]

df = None
for path in possible_paths:
    try:
        if os.path.exists(path):
            df = pd.read_csv(path)
            print(f"✅ Found CSV file at: {path}")
            break
    except Exception as e:
        print(f"❌ Error reading {path}: {e}")
        continue

if df is None:
    print("\n❌ ERROR: Could not find CSV file!")
    print(f"\nCurrent directory: {os.getcwd()}")
    print("\nFiles in current directory:")
    for file in os.listdir('.'):
        print(f"  - {file}")
    if os.path.exists('data'):
        print("\nFiles in data folder:")
        for file in os.listdir('data'):
            print(f"  - data/{file}")
    exit(1)

# Convert date to datetime
df['date'] = pd.to_datetime(df['date'])

print("\n" + "="*50)
print("✅ Data loaded successfully!")
print("="*50)
print(f"Shape: {df.shape}")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print(f"Columns: {list(df.columns)}")
print(f"Traffic sources: {df['source'].unique()}")
print(f"Pages: {df['page'].unique()}")

# ============================================================================
# TASK 1: TRAFFIC TREND PLOTS (matplotlib)
# ============================================================================

print("\n📊 Generating Matplotlib visualizations...")

# 1.1 Daily Total Traffic Trend
try:
    plt.figure(figsize=(12, 6))
    daily_total = df.groupby('date')['visits'].sum().reset_index()
    plt.plot(daily_total['date'], daily_total['visits'], 
             marker='o', linewidth=2, markersize=8, color='#2E86AB')
    plt.title('Daily Total Website Traffic', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Total Visits', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('visualizations/daily_traffic_trend.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✅ Daily traffic trend saved")
except Exception as e:
    print(f"  ❌ Error creating daily traffic trend: {e}")

# 1.2 Traffic by Source Trend
try:
    plt.figure(figsize=(14, 7))
    source_trend = df.pivot_table(index='date', columns='source', values='visits', aggfunc='sum')
    for source in source_trend.columns:
        plt.plot(source_trend.index, source_trend[source], 
                 marker='o', linewidth=2, markersize=6, label=source)
    plt.title('Daily Traffic Trends by Source', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Visits', fontsize=12)
    plt.legend(title='Traffic Source', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('visualizations/traffic_by_source_trend.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✅ Traffic by source trend saved")
except Exception as e:
    print(f"  ❌ Error creating traffic by source trend: {e}")

# 1.3 Traffic by Page Trend
try:
    plt.figure(figsize=(14, 7))
    page_trend = df.pivot_table(index='date', columns='page', values='visits', aggfunc='sum')
    for page in page_trend.columns:
        plt.plot(page_trend.index, page_trend[page], 
                 marker='s', linewidth=2, markersize=6, label=page)
    plt.title('Daily Traffic Trends by Page', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Visits', fontsize=12)
    plt.legend(title='Page', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('visualizations/traffic_by_page_trend.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✅ Traffic by page trend saved")
except Exception as e:
    print(f"  ❌ Error creating traffic by page trend: {e}")

# ============================================================================
# TASK 2: BOUNCE RATE HEATMAP (seaborn)
# ============================================================================

print("\n🔥 Generating Seaborn heatmaps...")

# 2.1 Bounce rate heatmap
try:
    bounce_pivot = df.pivot_table(
        index='page', 
        columns='source', 
        values='bounce_rate', 
        aggfunc='mean'
    )
    
    plt.figure(figsize=(10, 6))
    sns.heatmap(bounce_pivot, annot=True, fmt='.2f', cmap='YlOrRd', 
                linewidths=1, cbar_kws={'label': 'Bounce Rate'})
    plt.title('Bounce Rate Heatmap: Page vs Traffic Source', fontsize=16, fontweight='bold')
    plt.xlabel('Traffic Source', fontsize=12)
    plt.ylabel('Page', fontsize=12)
    plt.tight_layout()
    plt.savefig('visualizations/bounce_rate_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✅ Bounce rate heatmap saved")
except Exception as e:
    print(f"  ❌ Error creating bounce rate heatmap: {e}")

# 2.2 Unique visitors heatmap
try:
    unique_pivot = df.pivot_table(
        index='page', 
        columns='source', 
        values='unique_visitors', 
        aggfunc='mean'
    )
    
    plt.figure(figsize=(10, 6))
    sns.heatmap(unique_pivot, annot=True, fmt='.0f', cmap='Greens', 
                linewidths=1, cbar_kws={'label': 'Avg Unique Visitors'})
    plt.title('Average Unique Visitors: Page vs Traffic Source', fontsize=16, fontweight='bold')
    plt.xlabel('Traffic Source', fontsize=12)
    plt.ylabel('Page', fontsize=12)
    plt.tight_layout()
    plt.savefig('visualizations/unique_visitors_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✅ Unique visitors heatmap saved")
except Exception as e:
    print(f"  ❌ Error creating unique visitors heatmap: {e}")

# ============================================================================
# TASK 3: INTERACTIVE PLOTS (plotly)
# ============================================================================

print("\n📈 Generating Plotly interactive visualizations...")

# 3.1 Interactive Bar Chart
try:
    source_total = df.groupby('source')['visits'].sum().reset_index()
    fig1 = px.bar(source_total, x='source', y='visits', 
                  color='source', text='visits',
                  title='Total Visits by Traffic Source',
                  labels={'visits': 'Total Visits', 'source': 'Traffic Source'})
    fig1.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig1.update_layout(showlegend=False, height=500)
    fig1.write_html('visualizations/total_visits_by_source.html')
    print("  ✅ Interactive bar chart saved")
except Exception as e:
    print(f"  ❌ Error creating bar chart: {e}")

# 3.2 Interactive Pie Chart
try:
    fig2 = px.pie(source_total, values='visits', names='source', 
                  title='Traffic Distribution by Source',
                  hole=0.3)
    fig2.update_traces(textposition='inside', textinfo='percent+label')
    fig2.update_layout(height=500)
    fig2.write_html('visualizations/traffic_distribution_pie.html')
    print("  ✅ Interactive pie chart saved")
except Exception as e:
    print(f"  ❌ Error creating pie chart: {e}")

# 3.3 Interactive Line Chart
try:
    daily_source = df.groupby(['date', 'source'])['visits'].sum().reset_index()
    fig3 = px.line(daily_source, x='date', y='visits', color='source',
                   title='Daily Traffic Trends by Source',
                   markers=True,
                   labels={'visits': 'Visits', 'date': 'Date', 'source': 'Source'})
    fig3.update_layout(hovermode='x unified', height=500)
    fig3.write_html('visualizations/daily_trends_interactive.html')
    print("  ✅ Interactive line chart saved")
except Exception as e:
    print(f"  ❌ Error creating line chart: {e}")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

print("\n📊 Calculating summary statistics...")

try:
    total_visits = df['visits'].sum()
    total_unique = df['unique_visitors'].sum()
    avg_bounce = df['bounce_rate'].mean()
    
    # Save summary to text file
    with open('visualizations/summary_stats.txt', 'w') as f:
        f.write("WEB TRAFFIC ANALYSIS SUMMARY\n")
        f.write("="*30 + "\n")
        f.write(f"Period: Oct 13-19, 2025\n")
        f.write(f"Total Visits: {total_visits:,.0f}\n")
        f.write(f"Total Unique Visitors: {total_unique:,.0f}\n")
        f.write(f"Average Bounce Rate: {avg_bounce:.2%}\n\n")
        
        f.write("Top Pages by Visits:\n")
        page_totals = df.groupby('page')['visits'].sum().sort_values(ascending=False)
        for page, visits in page_totals.items():
            f.write(f"  {page}: {visits:,.0f}\n")
        
        f.write("\nTraffic Source Performance:\n")
        source_totals = df.groupby('source')['visits'].sum().sort_values(ascending=False)
        for source, visits in source_totals.items():
            bounce = df[df['source'] == source]['bounce_rate'].mean()
            f.write(f"  {source}: {visits:,.0f} visits ({bounce:.2%} bounce)\n")
    
    print("  ✅ Summary statistics saved")
    
    # Print to console too
    print("\n" + "="*50)
    print("📊 SUMMARY STATISTICS")
    print("="*50)
    print(f"Total Visits: {total_visits:,.0f}")
    print(f"Total Unique Visitors: {total_unique:,.0f}")
    print(f"Average Bounce Rate: {avg_bounce:.2%}")
    
except Exception as e:
    print(f"  ❌ Error creating summary stats: {e}")

# Final report
print("\n" + "="*50)
print("🏁 VISUALIZATION GENERATION COMPLETE!")
print("="*50)

# List all generated files
print("\n📁 Files in visualizations folder:")
if os.path.exists('visualizations'):
    files = os.listdir('visualizations')
    for file in sorted(files):
        size = os.path.getsize(f'visualizations/{file}')
        print(f"  📄 {file} ({size:,} bytes)")
    print(f"\n✅ Total files generated: {len(files)}")
else:
    print("  ❌ Visualizations folder not found!")

print("\n" + "="*50)