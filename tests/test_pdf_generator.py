import pytest
import json
import os
from reportlab.platypus import Table, Paragraph, ListFlowable, ListItem
from src.pipeline.pdf_generator import (PDFGenerator,
                                        generate_pdf_from_json,
                                        md_to_rml)


@pytest.fixture
def sample_json_data():
    """Fixture providing sample JSON data for testing"""
    return {
        "overall_tone_summary": {
            "general_emotional_direction": "Mostly negative",
            "positive_percentage": "17%",
            "negative_percentage": "33%",
            "neutral_percentage": "50%",
            "positive_count": 1,
            "negative_count": 2,
            "neutral_count": 3
        },
        "category_insights": {
            "inquiry": {
                "count": 3,
                "percentage": "50%"
            },
            "complaint": {
                "count": 2,
                "percentage": "33%"
            },
            "praise": {
                "count": 1,
                "percentage": "17%"
            }
        },
        "key_issues": [
            {
                "issue": "Customer dissatisfaction with feedback system",
                "supporting_messages": [
                    ("i was told by a customer our feedback system is "
                     "terrible")
                ]
            },
            {
                "issue": "Overwork and workload imbalance",
                "supporting_messages": [
                    ("im so overworked i have way too much on my plate "
                     "compared to my team")
                ]
            }
        ],
        "actionable_next_steps": [
            ("Investigate and address customer feedback regarding the "
             "feedback system."),
            ("Assess workload distribution across the team and adjust "
             "accordingly."),
            ("Implement a system for tracking workload and allocating "
             "tasks."),
            "Conduct regular team check-ins to address concerns.",
            ("Establish a process for collecting and addressing customer "
             "feedback.")
        ],
        "visuals": {
            "sentiment_bar_chart":
                "Positive: | \nNegative: ||| \nNeutral: ||||| \n"
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


def test_pdf_generator_overall_tone(sample_json_data, temp_output_path):
    """Test processing of overall tone section"""
    generator = PDFGenerator(temp_output_path)
    tone_data = sample_json_data['overall_tone_summary']
    elements = generator._process_overall_tone(tone_data)

    # Verify elements were generated
    assert len(elements) > 0
    # Verify table was created
    assert any(isinstance(e, Table) for e in elements)
    # Verify content
    assert any("Mostly negative" in str(e) for e in elements)


def test_pdf_generator_category_insights(sample_json_data, temp_output_path):
    """Test processing of category insights section"""
    generator = PDFGenerator(temp_output_path)
    category_data = sample_json_data['category_insights']
    elements = generator._process_category_insights(category_data)

    # Verify elements were generated
    assert len(elements) > 0
    # Verify table was created
    assert any(isinstance(e, Table) for e in elements)
    # Verify content
    assert any("Inquiry" in str(e) for e in elements)
    assert any("Complaint" in str(e) for e in elements)


def test_pdf_generator_key_issues(sample_json_data, temp_output_path):
    """Test processing of key issues section"""
    generator = PDFGenerator(temp_output_path)
    elements = generator._process_key_issues(sample_json_data['key_issues'])

    # Verify elements were generated
    assert len(elements) > 0
    # Verify content
    assert any("Customer dissatisfaction" in str(e) for e in elements)
    assert any("Overwork" in str(e) for e in elements)


def test_pdf_generator_action_items(sample_json_data, temp_output_path):
    generator = PDFGenerator(temp_output_path)
    action_data = sample_json_data['actionable_next_steps']
    elements = generator._process_action_items(action_data)

    assert len(elements) > 0

    text_blocks = []
    for e in elements:
        if isinstance(e, Paragraph):
            text_blocks.append(e.getPlainText())
        elif isinstance(e, ListFlowable):
            for sub in e._flowables:
                if isinstance(sub, ListItem):
                    for content in sub._flowables:
                        if isinstance(content, Paragraph):
                            text_blocks.append(content.getPlainText())
                elif isinstance(sub, Paragraph):
                    text_blocks.append(sub.getPlainText())
        elif hasattr(e, 'getPlainText'):
            text_blocks.append(e.getPlainText())

    print("Extracted text blocks:", text_blocks)
    assert any("Investigate and address" in t for t in text_blocks)


def test_pdf_generator_visuals(sample_json_data, temp_output_path):
    """Test processing of visuals section"""
    generator = PDFGenerator(temp_output_path)
    elements = generator._process_visuals(sample_json_data['visuals'])

    # Verify elements were generated
    assert len(elements) > 0
    # Verify content
    assert any("Positive: |" in str(e) for e in elements)
    assert any("Negative: |||" in str(e) for e in elements)


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

    # Test with non-dictionary input
    with pytest.raises(ValueError):
        generator.generate_report([])
