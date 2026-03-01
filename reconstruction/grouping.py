import torch
import torch.nn.functional as F
from typing import List, Dict, Optional
import numpy as np


class FragmentGrouper:
    """
    Groups fragmented disk blocks into coherent files using a mixed approach:
    sequential disk offsets + AI sequence scoring with a 1MB search radius.
    Supports parallel reconstruction for overlapping or interleaved files.
    """

    def __init__(self, classifier: Optional[torch.nn.Module] = None, 
                 search_radius: int = 1048576, 
                 block_size: int = 512):
        """
        Args:
            classifier: Optional FragmentClassifier model for sequence scoring.
            search_radius: Max distance (bytes) to search for the next fragment.
            block_size: Standard disk block size (default 512).
        """
        self.classifier = classifier
        self.search_radius = search_radius
        self.block_size = block_size
        self.device = "cpu"
        if classifier:
            try:
                self.device = next(classifier.parameters()).device
            except StopIteration:
                pass

    def score_sequence(self, fragment_data: bytes, target_type: str) -> float:
        """
        Uses AI to score how well a fragment matches a target file type.
        """
        if not self.classifier:
            return 0.5  # Neutral if no classifier
        
        # Labels must match HybridCarver and training data
        labels = ["jpeg", "pdf", "other"]
        if target_type not in labels:
            return 0.0
        
        target_idx = labels.index(target_type)
        
        # Preprocess fragment data
        padded = fragment_data.ljust(512, b"\x00")[:512]
        fragment_tensor = torch.tensor(list(padded), dtype=torch.float32) / 255.0
        fragment_tensor = fragment_tensor.unsqueeze(0).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            output = self.classifier(fragment_tensor)
            probabilities = F.softmax(output, dim=1)
            return probabilities[0, target_idx].item()

    def group_fragments(self, fragments: List[Dict]) -> List[Dict]:
        """
        Groups fragments into potential files.
        Input: list of { 'offset': int, 'data': bytes, 'identification': dict }
        Output: list of { 'id': int, 'type': str, 'data': bytes, 'fragment_offsets': list }
        """
        if not fragments:
            return []

        # Sort fragments by disk offset
        sorted_frags = sorted(fragments, key=lambda x: x['offset'])
        
        streams = []
        
        for frag in sorted_frags:
            ident = frag.get('identification', {})
            frag_type = ident.get('type', 'other')
            is_header = ident.get('source') == 'signature'
            
            # 1. Branching: New headers always start a new reconstruction path
            if is_header:
                new_stream = {
                    'id': len(streams),
                    'type': frag_type,
                    'fragments': [frag],
                    'last_offset': frag['offset'],
                    'complete': False
                }
                streams.append(new_stream)
            
            # 2. Parallel reconstruction: Try to attach this fragment to all compatible active streams
            for stream in streams:
                if stream['complete']:
                    continue
                
                # Don't re-add the fragment that just started this stream
                if len(stream['fragments']) == 1 and stream['fragments'][0]['offset'] == frag['offset']:
                    continue
                
                dist = frag['offset'] - stream['last_offset']
                
                # Must be forward in time and within search radius
                if 0 < dist <= self.search_radius:
                    is_sequential = dist == self.block_size
                    type_match = frag_type == stream['type']
                    
                    # AI sequence scoring as fallback/reinforcement
                    ai_score = 0.0
                    if not type_match and self.classifier:
                        ai_score = self.score_sequence(frag['data'], stream['type'])
                    
                    # Mixed Decision Logic
                    should_attach = False
                    
                    # Priority 1: Sequential and matching type (or sequential unclassified)
                    # BUT: Never attach if it's a known different type
                    if is_sequential and (type_match or frag_type == 'other'):
                        should_attach = True
                    
                    # Guard: Never attach all-zero blocks to a stream (wasteful and often wrong)
                    if ident.get('source') == 'zero_block':
                        should_attach = False
                    # Priority 2: Matches type within search radius
                    elif type_match:
                        should_attach = True
                    # Priority 3: High AI score for the stream's type
                    elif ai_score > 0.8:
                        should_attach = True
                    
                    # Hard Guard: Never attach a known different type to this stream
                    if frag_type != 'other' and frag_type != stream['type']:
                        should_attach = False
                        
                    if should_attach:
                        # Avoid adding the same offset twice to the same stream
                        if not any(f['offset'] == frag['offset'] for f in stream['fragments']):
                            stream['fragments'].append(frag)
                            stream['last_offset'] = frag['offset']
                            
                            # Check for footer (best effort)
                            if self._is_footer(frag, stream['type']):
                                stream['complete'] = True
        
        # 3. Finalize streams: Zero-fill gaps and aggregate
        results = []
        for stream in streams:
            reassembled_data = self._reassemble_with_gaps(stream['fragments'])
            results.append({
                'id': stream['id'],
                'type': stream['type'],
                'data': reassembled_data,
                'fragment_offsets': [f['offset'] for f in stream['fragments']],
                'completed': stream['complete']
            })
            
        return results

    def _is_footer(self, fragment: Dict, file_type: str) -> bool:
        """Checks if a fragment contains a known file footer."""
        ident = fragment.get('identification', {})
        frag_type = ident.get('type', 'other')
        
        # Only fragments identified as the target type can be footers
        if frag_type != file_type:
            return False
            
        data = fragment.get('data', b"")
        if file_type == 'jpeg':
            # JPEG footer is EOI (0xFF 0xD9)
            return b"\xff\xd9" in data
        if file_type == 'pdf':
            # PDF footer is %%EOF
            return b"%%EOF" in data
        return False

    def _reassemble_with_gaps(self, fragments: List[Dict]) -> bytes:
        """Reassembles fragments, filling gaps with zeros."""
        if not fragments:
            return b""
        
        # Ensure fragments are sorted by offset
        sorted_fragments = sorted(fragments, key=lambda x: x['offset'])
        
        result = bytearray()
        # Start from the first fragment's offset
        current_disk_pos = sorted_fragments[0]['offset']
        
        for frag in sorted_fragments:
            offset = frag['offset']
            data = frag['data']
            
            # Fill gap if current position is behind the next fragment
            if offset > current_disk_pos:
                gap_size = offset - current_disk_pos
                result.extend(b"\x00" * gap_size)
            
            # If for some reason we have overlapping data in the same stream (shouldn't happen with our logic)
            # we skip the overlapping part
            if offset < current_disk_pos:
                overlap = current_disk_pos - offset
                if overlap < len(data):
                    result.extend(data[overlap:])
                # else: entirely redundant, skip
            else:
                result.extend(data)
            
            current_disk_pos = offset + len(data)
            
        return bytes(result)
