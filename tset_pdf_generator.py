from src.pipeline.pdf_generator import generate_pdf_from_json

def test_pdf_generation():
    # Input and output file paths
    input_json = "testInsights.json"
    output_pdf = "feedback_report.pdf"
    
    # Generate the PDF
    generate_pdf_from_json(input_json, output_pdf)
    print(f"PDF generated successfully: {output_pdf}")

if __name__ == "__main__":
    test_pdf_generation()
