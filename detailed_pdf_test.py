import requests
import json
import re

def detailed_pdf_analysis():
    """Detailed analysis of the edited PDF content"""
    base_url = "https://legal-rag-fix.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    # Generate a simple contract
    contract_data = {
        "contract_type": "NDA",
        "jurisdiction": "US",
        "parties": {
            "party1_name": "Test Company",
            "party1_type": "corporation",
            "party2_name": "Test Person",
            "party2_type": "individual"
        },
        "terms": {
            "purpose": "Simple test",
            "duration": "1_year"
        },
        "special_clauses": []
    }
    
    print("🔍 Generating contract...")
    response = requests.post(f"{api_url}/generate-contract", json=contract_data, timeout=60)
    
    if response.status_code != 200:
        print(f"❌ Failed to generate contract: {response.status_code}")
        return False
    
    contract = response.json()['contract']
    print(f"✅ Contract generated: {contract['id']}")
    
    # Create edited version with minimal changes
    edited_contract = contract.copy()
    edited_contract['content'] = "EDITED CONTRACT CONTENT: This is a test of the edited PDF functionality."
    
    # Generate edited PDF
    edited_pdf_data = {"contract": edited_contract}
    
    print("🔍 Generating edited PDF...")
    pdf_response = requests.post(
        f"{api_url}/contracts/download-pdf-edited", 
        json=edited_pdf_data, 
        headers={'Content-Type': 'application/json'}, 
        timeout=30
    )
    
    if pdf_response.status_code != 200:
        print(f"❌ Failed to generate edited PDF: {pdf_response.status_code}")
        print(f"   Error: {pdf_response.text}")
        return False
    
    print(f"✅ Edited PDF generated successfully")
    print(f"   PDF Size: {len(pdf_response.content)} bytes")
    
    # Extract text content from PDF
    try:
        pdf_content = pdf_response.content.decode('latin-1', errors='ignore')
        
        # Look for text content in the PDF (between BT and ET markers)
        text_blocks = re.findall(r'BT\s+(.*?)\s+ET', pdf_content, re.DOTALL)
        
        print(f"\n📄 Found {len(text_blocks)} text blocks in PDF:")
        
        for i, block in enumerate(text_blocks):
            print(f"\n   Text Block {i+1}:")
            # Clean up the text block to show readable content
            lines = block.split('\n')
            for line in lines:
                if 'Tj' in line or 'TJ' in line:
                    # Extract text from PDF text operators
                    text_match = re.search(r'\((.*?)\)', line)
                    if text_match:
                        text = text_match.group(1)
                        print(f"     - {text}")
        
        # Also look for the word "Edited" anywhere in the PDF
        if 'Edited' in pdf_content:
            print(f"\n✅ Found 'Edited' text in PDF content")
            # Find the context around "Edited"
            edited_pos = pdf_content.find('Edited')
            context = pdf_content[max(0, edited_pos-100):edited_pos+100]
            print(f"   Context: ...{context}...")
            return True
        else:
            print(f"\n❌ 'Edited' text not found in PDF content")
            return False
            
    except Exception as e:
        print(f"❌ Error analyzing PDF: {str(e)}")
        return False

if __name__ == "__main__":
    success = detailed_pdf_analysis()
    if success:
        print("\n🎉 Detailed PDF analysis PASSED!")
    else:
        print("\n❌ Detailed PDF analysis FAILED!")