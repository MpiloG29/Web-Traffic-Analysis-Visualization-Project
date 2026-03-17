"""

generate_pdf_report_fixed.py - PDF Report without Unicode characters

"""
 
import pandas as pd

from fpdf import FPDF

import os

from datetime import datetime

import argparse
 
class PDFReport(FPDF):

    def header(self):

        self.set_font('Helvetica', 'B', 16)

        self.cell(0, 10, 'Web Traffic Analysis Report', 0, 1, 'C')

        self.ln(5)

    def footer(self):

        self.set_y(-15)

        self.set_font('Helvetica', 'I', 8)

        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):

        self.set_font('Helvetica', 'B', 14)

        self.set_fill_color(230, 240, 255)

        self.cell(0, 10, title, 0, 1, 'L', 1)

        self.ln(5)

    def chapter_body(self, text):

        self.set_font('Helvetica', '', 11)

        self.multi_cell(0, 8, text)

        self.ln(5)

    def add_image(self, image_path, caption=''):

        if os.path.exists(image_path):

            try:

                self.image(image_path, x=10, w=190)

                if caption:

                    self.set_font('Helvetica', 'I', 9)

                    self.cell(0, 8, caption, 0, 1, 'C')

                self.ln(5)

                return True

            except:

                return False

        return False
 
def generate_pdf_report(csv_path, output_path):

    print("=" * 60)

    print("📊 WEB TRAFFIC PDF REPORT GENERATOR")

    print("=" * 60)

    # Load data

    print("\n📁 Loading data...")

    df = pd.read_csv(csv_path)

    df['date'] = pd.to_datetime(df['date'])

    # Calculate statistics

    total_visits = df['visits'].sum()

    total_unique = df['unique_visitors'].sum()

    avg_bounce = df['bounce_rate'].mean() * 100

    date_range = f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"

    print(f"  Period: {date_range}")

    print(f"  Total Visits: {total_visits:,}")

    print(f"  Total Unique: {total_unique:,}")

    print(f"  Avg Bounce Rate: {avg_bounce:.1f}%")

    # Create PDF

    print("\n📄 Creating PDF document...")

    pdf = PDFReport()

    pdf.add_page()

    # Title Page

    pdf.set_font('Helvetica', 'B', 24)

    pdf.cell(0, 30, 'WEB TRAFFIC ANALYSIS', 0, 1, 'C')

    pdf.set_font('Helvetica', 'B', 18)

    pdf.cell(0, 15, 'Automated Report', 0, 1, 'C')

    pdf.ln(20)

    pdf.set_font('Helvetica', '', 12)

    pdf.cell(0, 10, f"Report Period: {date_range}", 0, 1, 'C')

    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, 'C')

    pdf.ln(20)

    # Executive Summary (without bullet points)

    pdf.add_page()

    pdf.chapter_title('Executive Summary')

    summary_text = f"""

PERIOD: {date_range}
 
KEY METRICS:

- Total Visits: {total_visits:,}

- Unique Visitors: {total_unique:,}

- Average Bounce Rate: {avg_bounce:.1f}%

"""

    pdf.chapter_body(summary_text)

    # Top Pages

    pdf.chapter_title('Top Pages by Visits')

    top_pages = df.groupby('page')['visits'].sum().sort_values(ascending=False)

    pages_text = ""

    for page, visits in top_pages.items():

        pages_text += f"- {page}: {visits:,} visits\n"

    pdf.chapter_body(pages_text)

    # Traffic Sources

    pdf.chapter_title('Traffic Source Performance')

    source_stats = df.groupby('source').agg({

        'visits': 'sum',

        'bounce_rate': 'mean'

    })

    sources_text = ""

    for source, row in source_stats.iterrows():

        sources_text += f"- {source}: {row['visits']:,} visits (Bounce: {row['bounce_rate']*100:.1f}%)\n"

    pdf.chapter_body(sources_text)

    # Daily Summary

    pdf.chapter_title('Daily Traffic Summary')

    daily = df.groupby('date')['visits'].sum()

    daily_text = ""

    for date, visits in daily.items():

        daily_text += f"- {date.strftime('%Y-%m-%d')}: {visits:,} visits\n"

    pdf.chapter_body(daily_text)

    # Add visualizations if they exist

    viz_files = [

        'visualizations/daily_traffic_trend.png',

        'visualizations/traffic_by_source_trend.png',

        'visualizations/traffic_by_page_trend.png',

        'visualizations/bounce_rate_heatmap.png',

        'visualizations/unique_visitors_heatmap.png'

    ]

    existing_viz = [f for f in viz_files if os.path.exists(f)]

    if existing_viz:

        pdf.add_page()

        pdf.chapter_title('Traffic Visualizations')

        for img_path in existing_viz:

            caption = os.path.basename(img_path).replace('_', ' ').replace('.png', '')

            pdf.add_image(img_path, caption)

    # Save PDF

    print("\n💾 Saving PDF...")

    pdf.output(output_path)

    file_size = os.path.getsize(output_path)

    print(f"\n✅ PDF Report generated successfully!")

    print(f"  📁 Location: {output_path}")

    print(f"  📊 File size: {file_size:,} bytes")
 
if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('--csv', required=True, help='Path to CSV file')

    parser.add_argument('--output', default='WebTraffic_Report.pdf', help='Output PDF path')

    args = parser.parse_args()

    generate_pdf_report(args.csv, args.output)
 