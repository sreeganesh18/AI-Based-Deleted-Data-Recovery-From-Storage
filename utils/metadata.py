import json
import os
from typing import List, Dict, Any, Optional


class MetadataManager:
    """
    Manages metadata for file fragments, original data, and reconstructed files.
    Tracks fragment IDs, source offsets, sizes, and file types.
    """

    def __init__(self, metadata_path: str = "dataset/metadata.json"):
        self.metadata_path = metadata_path
        self.data: Dict[str, Any] = {
            "fragments": {},
            "original_files": {},
            "reconstructed_files": {}
        }
        self.load()

    def load(self) -> None:
        """Loads metadata from the JSON file."""
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, 'r') as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, IOError):
                # If file is corrupt or unreadable, start with empty data
                pass

    def save(self) -> None:
        """Saves metadata to the JSON file."""
        os.makedirs(os.path.dirname(self.metadata_path), exist_ok=True)
        with open(self.metadata_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def add_fragment(self, fragment_id: str, metadata: Dict[str, Any]) -> None:
        """Adds or updates a fragment's metadata."""
        self.data["fragments"][fragment_id] = metadata
        self.save()

    def get_fragment(self, fragment_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves metadata for a specific fragment."""
        return self.data["fragments"].get(fragment_id)

    def list_fragments(self) -> List[str]:
        """Returns a list of all fragment IDs."""
        return list(self.data["fragments"].keys())

    def add_original_file(self, file_path: str, metadata: Dict[str, Any]) -> None:
        """Adds or updates metadata for an original file."""
        self.data["original_files"][file_path] = metadata
        self.save()

    def add_reconstructed_file(self, file_path: str, metadata: Dict[str, Any]) -> None:
        """Adds or updates metadata for a reconstructed file."""
        self.data["reconstructed_files"][file_path] = metadata
        self.save()
