"""测试文件工具函数。

验证 file_utils 模块中的文件操作工具函数。
"""

import pytest
from pathlib import Path
from wiki_generator.utils.file_utils import (
    ensure_directory,
    copy_file_or_directory,
    list_files,
    get_relative_path,
    backup_file,
    read_file_content,
    write_file_content,
)


class TestEnsureDirectory:
    """测试 ensure_directory 函数。"""

    def test_create_new_directory(self, tmp_path):
        """测试创建新目录。"""
        new_dir = tmp_path / "new_directory"
        ensure_directory(new_dir)
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_existing_directory(self, tmp_path):
        """测试已存在的目录。"""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        ensure_directory(existing_dir)
        assert existing_dir.exists()

    def test_nested_directories(self, tmp_path):
        """测试创建嵌套目录。"""
        nested = tmp_path / "level1" / "level2" / "level3"
        ensure_directory(nested)
        assert nested.exists()


class TestCopyFileOrDirectory:
    """测试 copy_file_or_directory 函数。"""

    def test_copy_file(self, tmp_path):
        """测试复制文件。"""
        src = tmp_path / "source.txt"
        dst = tmp_path / "destination.txt"
        src.write_text("test content")

        result = copy_file_or_directory(src, dst)
        assert result is True
        assert dst.exists()
        assert dst.read_text() == "test content"

    def test_copy_directory(self, tmp_path):
        """测试复制目录。"""
        src = tmp_path / "source_dir"
        dst = tmp_path / "dest_dir"
        src.mkdir()
        (src / "file.txt").write_text("content")

        result = copy_file_or_directory(src, dst)
        assert result is True
        assert dst.exists()
        assert (dst / "file.txt").exists()

    def test_copy_nonexistent_source(self, tmp_path):
        """测试复制不存在的源。"""
        src = tmp_path / "nonexistent"
        dst = tmp_path / "dest"
        result = copy_file_or_directory(src, dst)
        assert result is False

    def test_copy_without_overwrite(self, tmp_path):
        """测试不覆盖已存在的文件。"""
        src = tmp_path / "source.txt"
        dst = tmp_path / "dest.txt"
        src.write_text("new")
        dst.write_text("old")

        result = copy_file_or_directory(src, dst, overwrite=False)
        assert result is False
        assert dst.read_text() == "old"

    def test_copy_with_overwrite(self, tmp_path):
        """测试覆盖已存在的文件。"""
        src = tmp_path / "source.txt"
        dst = tmp_path / "dest.txt"
        src.write_text("new")
        dst.write_text("old")

        result = copy_file_or_directory(src, dst, overwrite=True)
        assert result is True
        assert dst.read_text() == "new"


class TestListFiles:
    """测试 list_files 函数。"""

    def test_list_files_in_directory(self, tmp_path):
        """测试列出目录中的文件。"""
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.txt").write_text("content2")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file3.txt").write_text("content3")

        files = list_files(tmp_path)
        assert len(files) == 3
        assert "file1.txt" in files
        assert "subdir/file3.txt" in files

    def test_list_files_with_pattern(self, tmp_path):
        """测试使用模式匹配文件。"""
        (tmp_path / "test1.txt").write_text("content1")
        (tmp_path / "test2.md").write_text("content2")
        (tmp_path / "other.txt").write_text("content3")

        files = list_files(tmp_path, pattern="test*.txt")
        assert len(files) == 2
        assert "test1.txt" in files
        assert "test2.txt" in files
        assert "other.txt" not in files

    def test_list_files_in_nonexistent_directory(self, tmp_path):
        """测试列出不存在目录中的文件。"""
        files = list_files(tmp_path / "nonexistent")
        assert files == []


class TestGetRelativePath:
    """测试 get_relative_path 函数。"""

    def test_relative_path(self, tmp_path):
        """测试计算相对路径。"""
        source = tmp_path / "level1" / "level2" / "file.txt"
        target = tmp_path / "level1"

        relative = get_relative_path(source, target)
        assert str(relative) == "level2/file.txt"

    def test_no_common_ancestor(self, tmp_path):
        """测试没有共同祖先的路径。"""
        source = tmp_path / "source" / "file.txt"
        target = Path("/other/path")

        relative = get_relative_path(source, target)
        assert relative == source.absolute()


class TestBackupFile:
    """测试 backup_file 函数。"""

    def test_backup_existing_file(self, tmp_path):
        """测试备份已存在的文件。"""
        original = tmp_path / "file.txt"
        original.write_text("original content")

        backup = backup_file(original)
        assert backup is not None
        assert backup.exists()
        assert backup.name == "file.txt.backup"
        assert backup.read_text() == "original content"

    def test_backup_nonexistent_file(self, tmp_path):
        """测试备份不存在的文件。"""
        backup = backup_file(tmp_path / "nonexistent.txt")
        assert backup is None


class TestReadFileContent:
    """测试 read_file_content 函数。"""

    def test_read_existing_file(self, tmp_path):
        """测试读取已存在的文件。"""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test content", encoding="utf-8")

        content = read_file_content(file_path)
        assert content == "test content"

    def test_read_nonexistent_file(self, tmp_path):
        """测试读取不存在的文件。"""
        content = read_file_content(tmp_path / "nonexistent.txt")
        assert content is None


class TestWriteFileContent:
    """测试 write_file_content 函数。"""

    def test_write_to_new_file(self, tmp_path):
        """测试写入新文件。"""
        file_path = tmp_path / "new_file.txt"
        result = write_file_content(file_path, "new content")

        assert result is True
        assert file_path.exists()
        assert file_path.read_text(encoding="utf-8") == "new content"

    def test_write_to_existing_file(self, tmp_path):
        """测试覆盖已存在的文件。"""
        file_path = tmp_path / "file.txt"
        file_path.write_text("old content")

        result = write_file_content(file_path, "new content")
        assert result is True
        assert file_path.read_text(encoding="utf-8") == "new content"

    def test_write_creates_parent_directories(self, tmp_path):
        """测试写入时创建父目录。"""
        file_path = tmp_path / "level1" / "level2" / "file.txt"
        result = write_file_content(file_path, "content")

        assert result is True
        assert file_path.exists()
        assert file_path.parent.exists()
