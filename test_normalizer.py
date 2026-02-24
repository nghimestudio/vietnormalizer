#!/usr/bin/env python3
"""
Simple test script for Vietnamese Normalizer library.
"""

from vietnormalizer import VietnameseNormalizer

def main():
    """Test the Vietnamese normalizer."""
    print("Initializing Vietnamese Normalizer...")
    normalizer = VietnameseNormalizer()
    
    test_cases = [
        "Hôm nay là 25/12/2023",
        "Cuộc họp lúc 14:30",
        "Giá là 1.500.000 đồng",
        "Tăng 25% so với năm ngoái",
        "Tôi có 123 quyển sách",
        "Sinh nhật vào 15/08/1990",
    ]
    
    print("\n" + "="*60)
    print("Testing Vietnamese Text Normalization")
    print("="*60 + "\n")
    
    for i, text in enumerate(test_cases, 1):
        normalized = normalizer.normalize(text)
        print(f"Test {i}:")
        print(f"  Input:    {text}")
        print(f"  Output:   {normalized}")
        print()

if __name__ == "__main__":
    main()

