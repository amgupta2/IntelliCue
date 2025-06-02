from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListItem, ListFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
import json
from datetime import datetime
import re

# Markdown to ReportLab conversion patterns
MD_REPLACEMENTS = [
    # bold **text**
    (re.compile(r'\*\*(.*?)\*\*'), r'<b>\1</b>'),
    # italic *text* (ignore list bullets that start with *)
    (re.compile(r'(?<!\n)\*(?!\s)(.*?)\*(?!\w)'), r'<i>\1</i>'),
    # line breaks inside list items
    (re.compile(r'\n\s*'), r'<br/>'),
]

def md_to_rml(text: str) -> str:
    """Convert markdown to ReportLab markup language"""
    for rgx, repl in MD_REPLACEMENTS:
        text = rgx.sub(repl, text)
    return text

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
            fontSize=26,
            textColor=colors.HexColor('#1A5276'),
            spaceAfter=24,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1A5276'),
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomSubHeading',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#1A5276'),
            spaceAfter=8
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            spaceAfter=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBullet',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            leftIndent=20,
            spaceAfter=6
        ))

    def _as_bullet_list(self, raw_lines):
        """Convert raw lines to a proper bullet list"""
        items = [
            ListItem(Paragraph(md_to_rml(line.strip()), self.styles['CustomBody']), 
                    bulletColor=colors.HexColor("#34495E"))
            for line in raw_lines if line.strip()
        ]
        return ListFlowable(
            items,
            bulletType='bullet',
            start='•',
            bulletFontName='Helvetica',
            leftIndent=20
        )

    def _header_footer(self, canvas, doc):
        """Add header and footer to each page"""
        canvas.saveState()
        # Header
        canvas.setFillColor('#1A5276')
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawString(72, doc.pagesize[1] - 50, "IntelliCue — Confidential")
        # Footer: page numbers
        canvas.setFont('Helvetica', 9)
        canvas.drawString(doc.pagesize[0] - 100, 20 * mm, f"Page {doc.page}")
        canvas.restoreState()

    def generate_report(self, json_data):
        """Generate a PDF report from the provided JSON data"""
        # Validate input data
        if not json_data:
            raise ValueError("Empty JSON data provided")
        if not isinstance(json_data, dict):
            raise ValueError("Input must be a dictionary")
        
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
        elements.append(Paragraph("IntelliCue Feedback Report", self.styles['CustomTitle']))
        elements.append(Spacer(1, 12))
        
        # Add timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elements.append(Paragraph(f"Generated on: {current_time}", self.styles['CustomBody']))
        elements.append(Spacer(1, 24))
        
        # Process overall tone summary
        if 'overall_tone_summary' in json_data:
            elements.extend(self._process_overall_tone(json_data['overall_tone_summary']))
        
        # Process category insights
        if 'category_insights' in json_data:
            elements.extend(self._process_category_insights(json_data['category_insights']))
        
        # Process key issues
        if 'key_issues' in json_data:
            elements.extend(self._process_key_issues(json_data['key_issues']))
        
        # Process actionable next steps
        if 'actionable_next_steps' in json_data:
            elements.extend(self._process_action_items(json_data['actionable_next_steps']))
        
        # Process visuals if present
        if 'visuals' in json_data:
            elements.extend(self._process_visuals(json_data['visuals']))
        
        # Build the PDF with header and footer
        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer)

    def _process_overall_tone(self, tone_data):
        """Process the overall tone summary section"""
        elements = []
        
        elements.append(Paragraph("Overall Tone Summary", self.styles['CustomHeading']))
        elements.append(Spacer(1, 12))
        
        # Create a table for sentiment data
        data = [
            ["Metric", "Value"],
            ["General Emotional Direction", tone_data.get('general_emotional_direction', 'N/A')],
            ["Positive Percentage", tone_data.get('positive_percentage', '0%')],
            ["Negative Percentage", tone_data.get('negative_percentage', '0%')],
            ["Neutral Percentage", tone_data.get('neutral_percentage', '0%')],
            ["Positive Count", str(tone_data.get('positive_count', 0))],
            ["Negative Count", str(tone_data.get('negative_count', 0))],
            ["Neutral Count", str(tone_data.get('neutral_count', 0))]
        ]
        
        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A5276')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9F9')]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 24))
        
        return elements

    def _process_category_insights(self, category_data):
        """Process the category insights section"""
        elements = []
        
        elements.append(Paragraph("Category Insights", self.styles['CustomHeading']))
        elements.append(Spacer(1, 12))
        
        # Create a table for category data
        data = [["Category", "Count", "Percentage"]]
        for category, stats in category_data.items():
            data.append([
                category.capitalize(),
                str(stats.get('count', 0)),
                stats.get('percentage', '0%')
            ])
        
        table = Table(data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A5276')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9F9')]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 24))
        
        return elements

    def _process_key_issues(self, issues_data):
        """Process the key issues section"""
        elements = []
        
        elements.append(Paragraph("Key Issues", self.styles['CustomHeading']))
        elements.append(Spacer(1, 12))
        
        for issue in issues_data:
            # Add issue
            elements.append(Paragraph(md_to_rml(issue['issue']), self.styles['CustomSubHeading']))
            
            # Add supporting messages as bullet points
            if 'supporting_messages' in issue:
                elements.append(self._as_bullet_list(issue['supporting_messages']))
            
            elements.append(Spacer(1, 12))
        
        return elements

    def _process_action_items(self, action_items):
        """Process the actionable next steps section"""
        elements = []
        
        elements.append(Paragraph("Actionable Next Steps", self.styles['CustomHeading']))
        elements.append(Spacer(1, 12))
        
        elements.append(self._as_bullet_list(action_items))
        elements.append(Spacer(1, 24))
        
        return elements

    def _process_visuals(self, visuals_data):
        """Process the visuals section"""
        elements = []
        
        elements.append(Paragraph("Visual Summary", self.styles['CustomHeading']))
        elements.append(Spacer(1, 12))
        
        if 'sentiment_bar_chart' in visuals_data:
            # Add the bar chart as pre-formatted text
            elements.append(Paragraph(
                visuals_data['sentiment_bar_chart'].replace('\n', '<br/>'),
                self.styles['CustomBody']
            ))
        
        elements.append(Spacer(1, 24))
        
        return elements

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
