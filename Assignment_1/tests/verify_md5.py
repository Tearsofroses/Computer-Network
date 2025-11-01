"""
MD5 Checksum Verification Script
Verify file integrity after download
"""

import hashlib
import sys

def calculate_md5(filepath):
    """Calculate MD5 hash of a file"""
    md5_hash = hashlib.md5()
    
    try:
        with open(filepath, 'rb') as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(4096), b''):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python verify_md5.py <original_file> <downloaded_file>")
        sys.exit(1)
    
    original_file = sys.argv[1]
    downloaded_file = sys.argv[2]
    
    print(f"Calculating MD5 for original file: {original_file}")
    original_md5 = calculate_md5(original_file)
    print(f"Original MD5:   {original_md5}")
    
    print(f"\nCalculating MD5 for downloaded file: {downloaded_file}")
    downloaded_md5 = calculate_md5(downloaded_file)
    print(f"Downloaded MD5: {downloaded_md5}")
    
    print("\n" + "="*60)
    if original_md5 == downloaded_md5:
        print("✅ PASS: Files are identical! Content integrity verified.")
    else:
        print("❌ FAIL: Files are different!")
    print("="*60)
