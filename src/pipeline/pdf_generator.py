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
        if 'insights' not in json_data or not str(json_data['insights']).strip():
            raise ValueError("Missing or empty required 'insights' section")
        
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
        
        # Process insights
        if 'insights' in json_data:
            elements.extend(self._process_insights(json_data['insights']))
        
        # Process and add sentiment analysis
        if 'sentiment_analysis' in json_data:
            elements.extend(self._add_sentiment_section(json_data['sentiment_analysis']))
        
        # Process and add actionable items
        if 'action_items' in json_data:
            elements.extend(self._add_action_items_section(json_data['action_items']))
        
        # Build the PDF with header and footer
        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
    
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
                elements.append(Paragraph(md_to_rml(header), self.styles['CustomHeading']))
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
                    raw_lines = [l.lstrip('*').strip() for l in para.split('\n') if l.strip()]
                    elements.append(self._as_bullet_list(raw_lines))
                else:
                    # Regular paragraph
                    elements.append(Paragraph(md_to_rml(para.strip()), self.styles['CustomBody']))
                    elements.append(Spacer(1, 6))
        
        return elements
    
    def _add_sentiment_section(self, sentiment_data):
        """Add the sentiment analysis section to the PDF"""
        elements = []
        
        elements.append(Paragraph("Sentiment Analysis", self.styles['CustomHeading']))
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
    
    def _add_action_items_section(self, action_items):
        """Add the actionable items section to the PDF"""
        elements = []
        
        elements.append(Paragraph("Recommended Actions", self.styles['CustomHeading']))
        elements.append(Spacer(1, 12))
        
        for category, items in action_items.items():
            elements.append(Paragraph(md_to_rml(category), self.styles['CustomSubHeading']))
            elements.append(self._as_bullet_list(items))
            elements.append(Spacer(1, 12))
        
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
