import os
import re
import tarfile
from io import BytesIO
from typing import Dict, List
from datetime import datetime

from src.common.file import File

class VirtualFileSystem:
    def __init__(self):
        self.files: Dict[str, File] = {}
        self.current_directory = "/"
    
    def load_from_tar(self, tar_path: str):
        with open(tar_path, 'rb') as f:
            tar_content = f.read()
            
        tar_buffer = BytesIO(tar_content)
        with tarfile.open(fileobj=tar_buffer) as tar:
            self.files["/"] = File("/", b"", True, datetime.now().timestamp())
            
            for member in tar.getmembers():
                path = "/" + member.name.lstrip("./")
                
                # Create intermediate directories
                parts = path.split("/")
                current_path = ""
                for part in parts[:-1]:
                    if part:
                        current_path += "/" + part
                        if current_path not in self.files:
                            self.files[current_path] = File(
                                current_path, 
                                b"", 
                                True,
                                datetime.now().timestamp()
                            )
                
                if member.isdir():
                    self.files[path] = File(path, b"", True, member.mtime)
                else:
                    file_content = tar.extractfile(member).read() if tar.extractfile(member) else b""
                    self.files[path] = File(path, file_content, False, member.mtime)

    def _resolve_path(self, path: str) -> str:
        if not path:
            return self.current_directory
        if path.startswith("/"):
            return os.path.normpath(path)
        return os.path.normpath(os.path.join(self.current_directory, path))

    def ls(self, path: str = "") -> List[str]:
        target_path = self._resolve_path(path)
        
        if target_path not in self.files:
            return []
            
        if not self.files[target_path].is_directory:
            return [os.path.basename(target_path)]
            
        result = []
        for file_path in self.files:
            parent_dir = os.path.dirname(file_path)
            if parent_dir == target_path and file_path != target_path:  # Добавляем проверку file_path != target_path
                name = os.path.basename(file_path)
                if name:  # Добавляем проверку на пустое имя
                    result.append(name)
        return sorted(result)

    def cd(self, path: str) -> bool:
        new_path = self._resolve_path(path)
        
        if new_path not in self.files:
            return False
        
        if not self.files[new_path].is_directory:
            return False
            
        self.current_directory = new_path
        return True

    def rm(self, path: str) -> bool:
        target_path = self._resolve_path(path)
        
        if target_path not in self.files:
            return False
            
        # If directory, remove all children
        if self.files[target_path].is_directory:
            paths_to_remove = [p for p in self.files if p.startswith(target_path)]
            for p in paths_to_remove:
                del self.files[p]
        else:
            del self.files[target_path]
            
        return True

    def find(self, path: str, pattern: str) -> List[str]:
        target_path = self._resolve_path(path)
        if target_path not in self.files:
            return []
            
        results = []
        regex = re.compile(pattern)
        
        for file_path in self.files:
            if file_path.startswith(target_path):
                relative_path = file_path[len(target_path):].lstrip('/')
                if regex.search(relative_path):
                    results.append(file_path)
                    
        return sorted(results)