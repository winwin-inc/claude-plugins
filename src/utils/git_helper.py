"""
Git 操作辅助模块

提供 Git 仓库克隆、分支管理等操作。
"""

import os
import subprocess
from typing import Optional
from .error_handler import CommandInstallError
from .errors import ErrorCode
from .file_helper import FileHelper


class GitHelper:
    """Git 操作辅助类"""

    def __init__(self, timeout: int = 60):
        """
        初始化 Git 辅助类

        Args:
            timeout: 操作超时时间（秒）
        """
        self.timeout = timeout

    def clone(self, repo_url: str, target_dir: Optional[str] = None, depth: int = 1) -> str:
        """
        克隆 Git 仓库

        Args:
            repo_url: 仓库 URL
            target_dir: 目标目录（可选，默认为临时目录）
            depth: 克隆深度（1 表示浅克隆）

        Returns:
            克隆目录路径

        Raises:
            CommandInstallError: 克隆失败时
        """
        # 如果未指定目标目录，创建临时目录
        if target_dir is None:
            target_dir = FileHelper.create_temp_dir(prefix="git-clone-")

        try:
            # 构建克隆命令
            cmd = ["git", "clone", "--depth", str(depth), repo_url, target_dir]

            # 执行克隆
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=True
            )

            return target_dir

        except subprocess.TimeoutExpired:
            # 清理临时目录
            FileHelper.cleanup_temp_dir(target_dir)

            raise CommandInstallError(
                ErrorCode.DOWNLOAD_TIMEOUT,
                f"Git 克隆超时（{self.timeout}秒）: {repo_url}"
            )

        except subprocess.CalledProcessError as e:
            # 清理临时目录
            FileHelper.cleanup_temp_dir(target_dir)

            # 解析错误信息
            error_msg = e.stderr.strip() if e.stderr else "未知错误"

            raise CommandInstallError(
                ErrorCode.DOWNLOAD_GIT_CLONE_FAILED,
                f"Git 克隆失败: {repo_url}\n   {error_msg}"
            )

        except FileNotFoundError:
            # Git 未安装
            FileHelper.cleanup_temp_dir(target_dir)

            raise CommandInstallError(
                ErrorCode.DOWNLOAD_GIT_CLONE_FAILED,
                "未找到 Git 命令，请先安装 Git"
            )

        except Exception as e:
            # 清理临时目录
            FileHelper.cleanup_temp_dir(target_dir)

            raise CommandInstallError(
                ErrorCode.DOWNLOAD_GIT_CLONE_FAILED,
                f"克隆过程中发生意外错误: {str(e)}"
            )

    def get_latest_commit(self, repo_dir: str) -> Optional[str]:
        """
        获取仓库最新提交的 SHA

        Args:
            repo_dir: 仓库目录路径

        Returns:
            提交 SHA，失败返回 None
        """
        try:
            cmd = ["git", "rev-parse", "HEAD"]
            result = subprocess.run(
                cmd,
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=10,
                check=True
            )

            return result.stdout.strip()

        except Exception:
            return None

    def get_remote_url(self, repo_dir: str) -> Optional[str]:
        """
        获取仓库的远程 URL

        Args:
            repo_dir: 仓库目录路径

        Returns:
            远程 URL，失败返回 None
        """
        try:
            cmd = ["git", "config", "--get", "remote.origin.url"]
            result = subprocess.run(
                cmd,
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=10,
                check=True
            )

            return result.stdout.strip()

        except Exception:
            return None

    def is_git_repo(self, directory: str) -> bool:
        """
        检查目录是否是 Git 仓库

        Args:
            directory: 目录路径

        Returns:
            是否是 Git 仓库
        """
        git_dir = os.path.join(directory, ".git")
        return os.path.isdir(git_dir)

    def get_tags(self, repo_dir: str) -> list:
        """
        获取仓库的所有标签

        Args:
            repo_dir: 仓库目录路径

        Returns:
            标签列表
        """
        try:
            cmd = ["git", "tag", "-l"]
            result = subprocess.run(
                cmd,
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=10,
                check=True
            )

            tags = result.stdout.strip().split("\n")
            return [tag for tag in tags if tag]  # 过滤空字符串

        except Exception:
            return []

    def checkout_tag(self, repo_dir: str, tag: str) -> bool:
        """
        检出指定标签

        Args:
            repo_dir: 仓库目录路径
            tag: 标签名

        Returns:
            是否成功
        """
        try:
            cmd = ["git", "checkout", tag]
            subprocess.run(
                cmd,
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )

            return True

        except Exception:
            return False
