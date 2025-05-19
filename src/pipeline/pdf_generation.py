from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus import Table, TableStyle
from reportlab.lib.enums import TA_CENTER
import json
from datetime import datetime
import re


class PDFGenerator:
    def __init__(self, output_path):
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#2C3E50')
        ))

        self.styles.add(ParagraphStyle(
            name='CustomSubHeading',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            textColor=colors.HexColor('#34495E')
        ))

        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            leading=14
        ))

        self.styles.add(ParagraphStyle(
            name='CustomBullet',
            parent=self.styles['Normal'],
            fontSize=12,
            leftIndent=20,
            spaceAfter=6,
            leading=14
        ))

    def generate_report(self, json_data):
        """Generate a PDF report from the provided JSON data"""
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Container for PDF elements
        elements = []

        # Add title
        elements.append(Paragraph("IntelliCue Feedback Report",
                                  self.styles['CustomTitle']))
        elements.append(Spacer(1, 12))

        # Add timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elements.append(Paragraph(f"Generated on: {current_time}",
                                  self.styles['CustomBody']))
        elements.append(Spacer(1, 24))

        # Process insights
        if 'insights' in json_data:
            elements.extend(self._process_insights(json_data['insights']))

        # Process and add sentiment analysis
        if 'sentiment_analysis' in json_data:
            elements.extend(
                self._add_sentiment_section(
                    json_data['sentiment_analysis']))

        # Process and add actionable items
        if 'action_items' in json_data:
            elements.extend(
                self._add_action_items_section(
                    json_data['action_items']))

        # Build the PDF
        doc.build(elements)

    def _process_insights(self, insights_text):
        """Process the insights text and convert it to PDF elements"""
        elements = []

        # Split the text into sections based on markdown headers
        sections = re.split(r'\*\*(\d+\.\s*[^*]+):\*\*', insights_text)

        # Process each section
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                header = sections[i].strip()
                content = sections[i + 1].strip()

                # Add section header
                elements.append(
                    Paragraph(header, self.styles['CustomHeading']))
                elements.append(Spacer(1, 12))

                # Process content
                elements.extend(self._process_content(content))
                elements.append(Spacer(1, 24))

        return elements

    def _process_content(self, content):
        """Process content text and convert it to PDF elements"""
        elements = []

        # Split content into paragraphs
        paragraphs = content.split('\n\n')

        for para in paragraphs:
            if para.strip():
                # Check if it's a bullet point
                if para.strip().startswith('*'):
                    # Process bullet points
                    bullet_points = para.split('\n')
                    for point in bullet_points:
                        if point.strip():
                            # Remove the bullet point marker and clean up
                            clean_point = point.strip().lstrip('*').strip()
                            elements.append(
                                Paragraph(f"• {clean_point}",
                                          self.styles['CustomBullet']))
                else:
                    # Regular paragraph
                    elements.append(Paragraph(para.strip(),
                                              self.styles['CustomBody']))
                    elements.append(Spacer(1, 6))

        return elements

    def _add_sentiment_section(self, sentiment_data):
        """Add the sentiment analysis section to the PDF"""
        elements = []

        elements.append(Paragraph("Sentiment Analysis",
                                  self.styles['CustomHeading']))
        elements.append(Spacer(1, 12))

        # Create a table for sentiment data
        data = [["Category", "Positive", "Neutral", "Negative"]]
        for category, sentiments in sentiment_data.items():
            data.append([
                category,
                f"{sentiments.get('positive', 0)}%",
                f"{sentiments.get('neutral', 0)}%",
                f"{sentiments.get('negative', 0)}%"
            ])

        table = Table(data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ECC71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 24))

        return elements

    def _add_action_items_section(self, action_items):
        """Add the actionable items section to the PDF"""
        elements = []

        elements.append(Paragraph("Recommended Actions",
                                  self.styles['CustomHeading']))
        elements.append(Spacer(1, 12))

        for category, items in action_items.items():
            elements.append(Paragraph(category, self.styles['CustomHeading']))
            for item in items:
                elements.append(Paragraph(f"• {item}",
                                          self.styles['CustomBody']))
            elements.append(Spacer(1, 12))

        return elements


# Example usage:
def generate_pdf_from_json(json_file_path, output_pdf_path):
    """
    Generate a PDF report from a JSON file

    Args:
        json_file_path (str): Path to the input JSON file
        output_pdf_path (str): Path where the PDF should be saved
    """
    # Read JSON data
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    # Generate PDF
    generator = PDFGenerator(output_pdf_path)
    generator.generate_report(data)
