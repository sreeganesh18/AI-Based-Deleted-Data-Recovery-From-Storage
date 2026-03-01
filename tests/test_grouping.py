import pytest
from reconstruction.grouping import FragmentGrouper

def test_grouping_basic():
    """Test basic grouping without fragmentation or gaps."""
    grouper = FragmentGrouper()
    
    fragments = [
        {
            'offset': 0,
            'data': b"HEADER" + b"\x00"*506,
            'identification': {'type': 'jpeg', 'source': 'signature'}
        },
        {
            'offset': 512,
            'data': b"DATA" + b"\x00"*508,
            'identification': {'type': 'jpeg', 'source': 'ai'}
        }
    ]
    
    results = grouper.group_fragments(fragments)
    assert len(results) == 1
    assert results[0]['type'] == 'jpeg'
    assert len(results[0]['data']) == 1024
    assert results[0]['data'].startswith(b"HEADER")

def test_grouping_with_gaps():
    """Test that gaps are zero-filled."""
    grouper = FragmentGrouper()
    
    fragments = [
        {
            'offset': 0,
            'data': b"H" * 512,
            'identification': {'type': 'jpeg', 'source': 'signature'}
        },
        {
            'offset': 1024, # Gap of 512 bytes at 512
            'data': b"D" * 512,
            'identification': {'type': 'jpeg', 'source': 'ai'}
        }
    ]
    
    results = grouper.group_fragments(fragments)
    assert len(results) == 1
    assert len(results[0]['data']) == 1536
    # Check gap is zero-filled
    assert results[0]['data'][512:1024] == b"\x00" * 512
    assert results[0]['data'][1024:] == b"H" * 0 + b"D" * 512 # wait, 1024 to 1536 should be "D"

def test_parallel_reconstruction():
    """Test that multiple headers start multiple streams."""
    grouper = FragmentGrouper()
    
    fragments = [
        {
            'offset': 0,
            'data': b"J" * 512,
            'identification': {'type': 'jpeg', 'source': 'signature'}
        },
        {
            'offset': 512,
            'data': b"P" * 512,
            'identification': {'type': 'pdf', 'source': 'signature'}
        },
        {
            'offset': 1024,
            'data': b"j" * 512,
            'identification': {'type': 'jpeg', 'source': 'ai'}
        },
        {
            'offset': 1536,
            'data': b"p" * 512,
            'identification': {'type': 'pdf', 'source': 'ai'}
        }
    ]
    
    results = grouper.group_fragments(fragments)
    assert len(results) == 2
    
    jpeg_file = next(r for r in results if r['type'] == 'jpeg')
    pdf_file = next(r for r in results if r['type'] == 'pdf')
    
    assert len(jpeg_file['fragment_offsets']) == 2
    assert len(pdf_file['fragment_offsets']) == 2
    assert 0 in jpeg_file['fragment_offsets']
    assert 1024 in jpeg_file['fragment_offsets']
    assert 512 in pdf_file['fragment_offsets']
    assert 1536 in pdf_file['fragment_offsets']

def test_search_radius():
    """Test that search radius is respected."""
    # Set a small search radius for testing
    grouper = FragmentGrouper(search_radius=1024)
    
    fragments = [
        {
            'offset': 0,
            'data': b"H" * 512,
            'identification': {'type': 'jpeg', 'source': 'signature'}
        },
        {
            'offset': 2048, # 2048 - 0 = 2048 > 1024 radius
            'data': b"D" * 512,
            'identification': {'type': 'jpeg', 'source': 'ai'}
        }
    ]
    
    results = grouper.group_fragments(fragments)
    assert len(results) == 1
    assert len(results[0]['fragment_offsets']) == 1 # Second fragment should be ignored

def test_sequential_priority():
    """Test that sequential blocks are prioritized if multiple options exist."""
    # This is a bit harder to test without a more complex scenario, 
    # but we can verify that sequential 'other' blocks are picked up.
    grouper = FragmentGrouper()
    
    fragments = [
        {
            'offset': 0,
            'data': b"H" * 512,
            'identification': {'type': 'jpeg', 'source': 'signature'}
        },
        {
            'offset': 512,
            'data': b"O" * 512,
            'identification': {'type': 'other', 'source': 'ai'}
        }
    ]
    
    results = grouper.group_fragments(fragments)
    assert len(results) == 1
    assert 512 in results[0]['fragment_offsets']

def test_footer_detection():
    """Test that reconstruction stops after a footer."""
    grouper = FragmentGrouper()
    
    fragments = [
        {
            'offset': 0,
            'data': b"H" * 512,
            'identification': {'type': 'jpeg', 'source': 'signature'}
        },
        {
            'offset': 512,
            'data': b"F" * 510 + b"\xff\xd9",
            'identification': {'type': 'jpeg', 'source': 'ai'}
        },
        {
            'offset': 1024,
            'data': b"X" * 512,
            'identification': {'type': 'jpeg', 'source': 'ai'}
        }
    ]
    
    results = grouper.group_fragments(fragments)
    assert len(results) == 1
    assert len(results[0]['fragment_offsets']) == 2
    assert 1024 not in results[0]['fragment_offsets']
    assert results[0]['completed'] == True

if __name__ == "__main__":
    import sys
    # For --parallel flag mentioned in the plan
    # In a real scenario, this might trigger more intensive parallel tests
    print("Running FragmentGrouper tests...")
    # Just use pytest to run this file if executed directly
    import pytest
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
