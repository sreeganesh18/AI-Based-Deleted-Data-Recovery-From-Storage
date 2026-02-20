from typing import List, Dict


class SignatureCarver:
    """
    Initial scan for known file signatures.
    Currently scoped to JPEG files (FFD8 header, FFD9 footer).
    """

    JPEG_HEADER1 = b"\xff\xd8\xff\xe0"
    JPEG_HEADER2 = b"\xff\xd8\xff\xe1"
    JPEG_FOOTER = b"\xff\xd9"

    def __init__(self, block_size: int = 512):
        self.block_size = block_size
        self.in_file = False
        self.current_file_data = bytearray()
        self.start_offset = -1
        self.carved_files = []

    def process_block(self, offset: int, block: bytes):
        """
        Process a single data block to find JPEG headers and footers.
        """
        header_idx1 = block.find(self.JPEG_HEADER1)
        header_idx2 = block.find(self.JPEG_HEADER2)

        header_idx = -1
        if header_idx1 != -1 and header_idx2 != -1:
            header_idx = min(header_idx1, header_idx2)
        else:
            header_idx = max(header_idx1, header_idx2)

        if header_idx != -1 and not self.in_file:
            self.in_file = True
            self.start_offset = offset + header_idx
            self.current_file_data = bytearray(block[header_idx:])

            # Check if footer is also in the same block
            self._check_and_close_footer()
            return

        if self.in_file:
            self.current_file_data.extend(block)
            self._check_and_close_footer()

    def _check_and_close_footer(self):
        footer_idx = self.current_file_data.find(self.JPEG_FOOTER)
        if footer_idx != -1:
            end_idx = footer_idx + 2
            self.carved_files.append(
                {
                    "start_offset": self.start_offset,
                    "data": bytes(self.current_file_data[:end_idx]),
                }
            )
            self.in_file = False
            self.current_file_data = bytearray()

    def get_carved_files(self) -> List[Dict]:
        return self.carved_files
