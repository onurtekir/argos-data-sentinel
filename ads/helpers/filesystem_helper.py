from pathlib import Path


class FileSystemHelper:

    def create_parent_directories(self, path: Path) -> Path:
        path.mkdir(parents=True, exist_ok=True)
        return path