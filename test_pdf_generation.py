#!/usr/bin/env python3
"""
Simple test script for PDF generation
"""

from utils.pdf_generator import generate_security_pdf_report
import os

def test_pdf_generation():
    """Test PDF generation functionality"""
    print("🧪 Testing PDF Generation...")
    
    try:
        # Generate PDF report
        pdf_file = generate_security_pdf_report("test_session")
        
        if pdf_file and os.path.exists(pdf_file):
            print(f"✅ PDF generated successfully: {pdf_file}")
            print(f"📄 File size: {os.path.getsize(pdf_file)} bytes")
            print(f"📍 Full path: {os.path.abspath(pdf_file)}")
            return True
        else:
            print("❌ PDF file was not created")
            return False
            
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_generation()
    if success:
        print("\n🎉 PDF generation test passed!")
    else:
        print("\n💥 PDF generation test failed!") 