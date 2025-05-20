import pytest
import json
import os
from reportlab.platypus import Table
from src.pipeline.pdf_generator import PDFGenerator, generate_pdf_from_json, md_to_rml

@pytest.fixture
def sample_json_data():
    """Fixture providing sample JSON data for testing"""
    return {
        "insights": """
**1. Overall Tone:**
* The overall tone of the feedback is neutral
* No significant positive or negative sentiment detected
* Communication style is professional and balanced

**2. Key Issues:**
* No discernible issues were identified in the feedback
* All points raised are neutral in nature
* No urgent concerns requiring immediate attention
""",
        "sentiment_analysis": {
            "Communication": {
                "positive": 60,
                "neutral": 30,
                "negative": 10
            },
            "Work Environment": {
                "positive": 70,
                "neutral": 20,
                "negative": 10
            }
        },
        "action_items": {
            "Immediate Actions": [
                "Schedule follow-up meeting",
                "Review current processes"
            ],
            "Long-term Considerations": [
                "Monitor team dynamics",
                "Plan quarterly review"
            ]
        }
    }

@pytest.fixture
def temp_output_path(tmp_path):
    """Fixture providing a temporary output path for PDF files"""
    return str(tmp_path / "test_output.pdf")

def test_md_to_rml_conversion():
    """Test markdown to ReportLab markup conversion"""
    # Test bold text
    assert md_to_rml("**bold text**") == "<b>bold text</b>"
    
    # Test italic text
    assert md_to_rml("*italic text*") == "<i>italic text</i>"
    
    # Test line breaks
    assert md_to_rml("line1\nline2") == "line1<br/>line2"
    
    # Test multiple markdown elements
    text = "**bold** and *italic* with\nline break"
    expected = "<b>bold</b> and <i>italic</i> with<br/>line break"
    assert md_to_rml(text) == expected

def test_pdf_generator_initialization(temp_output_path):
    """Test PDFGenerator initialization"""
    generator = PDFGenerator(temp_output_path)
    assert generator.output_path == temp_output_path
    assert hasattr(generator, 'styles')
    assert 'CustomTitle' in generator.styles
    assert 'CustomBody' in generator.styles

def test_generate_pdf_from_json(sample_json_data, temp_output_path):
    """Test PDF generation from JSON data"""
    # Create a temporary JSON file
    json_path = temp_output_path.replace('.pdf', '.json')
    with open(json_path, 'w') as f:
        json.dump(sample_json_data, f)
    
    # Generate PDF
    generate_pdf_from_json(json_path, temp_output_path)
    
    # Verify PDF was created
    assert os.path.exists(temp_output_path)
    assert os.path.getsize(temp_output_path) > 0

def test_pdf_generator_process_insights(sample_json_data, temp_output_path):
    """Test processing of insights section"""
    generator = PDFGenerator(temp_output_path)
    elements = generator._process_insights(sample_json_data['insights'])
    
    # Verify elements were generated
    assert len(elements) > 0
    # Verify section headers are present
    assert any("Overall Tone" in str(e) for e in elements)
    assert any("Key Issues" in str(e) for e in elements)

def test_pdf_generator_process_content(temp_output_path):
    """Test processing of content with bullet points"""
    generator = PDFGenerator(temp_output_path)
    
    # Test regular paragraph
    content = "This is a regular paragraph."
    elements = generator._process_content(content)
    assert len(elements) == 2  # Paragraph + Spacer
    
    # Test bullet points
    content = "* First point\n* Second point"
    elements = generator._process_content(content)
    assert len(elements) == 1  # Single ListFlowable

def test_pdf_generator_sentiment_section(sample_json_data, temp_output_path):
    """Test sentiment analysis section generation"""
    generator = PDFGenerator(temp_output_path)
    elements = generator._add_sentiment_section(sample_json_data['sentiment_analysis'])
    
    # Verify elements were generated
    assert len(elements) > 0
    # Verify table was created
    assert any(isinstance(e, Table) for e in elements)

def test_pdf_generator_action_items(sample_json_data, temp_output_path):
    """Test action items section generation"""
    generator = PDFGenerator(temp_output_path)
    elements = generator._add_action_items_section(sample_json_data['action_items'])
    
    # Verify elements were generated
    assert len(elements) > 0
    # Verify categories are present
    assert any("Immediate Actions" in str(e) for e in elements)
    assert any("Long-term Considerations" in str(e) for e in elements)

def test_pdf_generator_full_report(sample_json_data, temp_output_path):
    """Test generation of complete report"""
    generator = PDFGenerator(temp_output_path)
    generator.generate_report(sample_json_data)
    
    # Verify PDF was created
    assert os.path.exists(temp_output_path)
    assert os.path.getsize(temp_output_path) > 0

def test_pdf_generator_error_handling(temp_output_path):
    """Test error handling for invalid input"""
    generator = PDFGenerator(temp_output_path)
    
    # Test with empty JSON
    with pytest.raises(ValueError):
        generator.generate_report({})
    
    # Test with missing required sections
    with pytest.raises(ValueError):
        generator.generate_report({"insights": ""}) 