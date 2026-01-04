# 命令来源解析机制研究报告

**版本**: 1.0.0
**创建日期**: 2025-01-03
**状态**: 完成版

---

## 1. 研究概述

### 1.1 研究目标

为 Claude Code 命令安装器设计并实现一个健壮的命令来源解析机制，支持以下三种来源类型：

1. **Git 仓库 URL**：远程 Git 仓库（HTTPS、SSH、Git 协议）
2. **本地文件路径**：相对路径或绝对路径
3. **预设命令名称**：预定义的命令名称映射

### 1.2 核心挑战

- **来源类型识别**：准确区分三种不同的来源类型
- **URL 格式多样性**：处理各种 Git URL 格式（GitHub、GitLab、Bitbucket 等）
- **路径解析复杂性**：处理相对路径、绝对路径、符号链接
- **边界情况**：处理看起来像一种类型但实际是另一种的情况
- **错误处理**：提供友好的错误消息和降级策略

---

## 2. 推荐方案：启发式分层检测

### 2.1 核心算法

采用**优先级分层检测**策略，按照以下顺序检测来源类型：

```
1. 本地路径检测（最高优先级）
   ↓
2. Git URL 检测
   ↓
3. 预设名称检测（最低优先级）
   ↓
4. 错误处理
```

**设计原理**：
- **本地路径优先**：避免误将本地路径识别为预设名称
- **Git URL 次之**：URL 格式明确且易于检测
- **预设名称最后**：作为兜底机制，避免过于宽泛的匹配

---

## 3. 来源类型识别

### 3.1 本地路径检测

#### 检测逻辑

```python
def is_local_path(source: str) -> bool:
    """
    检测是否为本地文件路径

    规则：
    1. 以 ./ 或 ../ 开头 → 相对路径
    2. 以 / 开头（Unix）或盘符开头（Windows）→ 绝对路径
    3. 包含路径分隔符且当前目录存在该路径
    """

    # 规则 1: 相对路径标记
    if source.startswith('./') or source.startswith('../'):
        return True

    # 规则 2: 绝对路径
    if source.startswith('/') or source.startswith('~'):
        return True

    # Windows 绝对路径 (C:\, D:\)
    if len(source) >= 2 and source[1] == ':':
        return True

    # 规则 3: 不包含 URL 特征字符，可能是相对路径
    # 如果包含 / 或 \\ 但不包含 :// 或 @:，检查路径是否存在
    if ('/' in source or '\\' in source) and not contains_url_markers(source):
        return os.path.exists(source)

    return False


def contains_url_markers(source: str) -> bool:
    """检查是否包含 URL 特征字符"""
    url_markers = ['://', 'git@', 'github.com', 'gitlab.com', 'bitbucket.org']
    return any(marker in source for marker in url_markers)
```

#### 边界情况处理

| 输入示例 | 识别结果 | 处理方式 |
|---------|---------|---------|
| `./commands/my-command.md` | ✅ 本地路径 | 直接解析为相对路径 |
| `../shared-command.md` | ✅ 本地路径 | 解析为父目录路径 |
| `/absolute/path/command.md` | ✅ 本地路径 | 使用绝对路径 |
| `~/commands/my-command.md` | ✅ 本地路径 | 展开为 home 目录 |
| `C:\commands\my-command.md` | ✅ 本地路径 | Windows 绝对路径 |
| `command-name` | ❌ 非本地路径 | 传递给下一层检测 |
| `https://github.com/user/repo` | ❌ 非本地路径 | 包含 :// 标记 |

### 3.2 Git URL 检测

#### 支持 Git URL 格式

基于 [Git 官方文档](https://git-scm.com/docs/git-config) 和 [LabEx 教程](https://labex.io/tutorials/git-how-to-validate-git-repository-url-434201)的研究结果：

| 协议类型 | URL 模式 | 示例 | 正则表达式 |
|---------|---------|------|-----------|
| **HTTPS** | `https://host/user/repo[.git]` | `https://github.com/user/repo` | `^https://.*` |
| **SSH** | `git@host:user/repo[.git]` | `git@github.com:user/repo.git` | `^git@.*:.*` |
| **Git 协议** | `git://host/user/repo[.git]` | `git://github.com/user/repo` | `^git://.*` |
| **带子目录** | `url/tree/branch/path` | `https://github.com/user/repo/tree/main/commands` | `^https://.*/tree/.*` |

#### 检测逻辑

```python
def is_git_url(source: str) -> tuple[bool, Optional[GitURLInfo]]:
    """
    检测是否为 Git 仓库 URL

    参考：
    - https://stackoverflow.com/questions/23976019/how-to-verify-valid-format-of-url-as-a-git-repo
    - https://labex.io/tutorials/git-how-to-validate-git-repository-url-434201
    """

    # HTTPS URL
    if source.startswith('https://') or source.startswith('http://'):
        return parse_https_url(source)

    # SSH URL (git@host:user/repo.git)
    if source.startswith('git@'):
        return parse_ssh_url(source)

    # Git 协议 (git://host/user/repo.git)
    if source.startswith('git://'):
        return parse_git_protocol_url(source)

    return False, None


def parse_https_url(source: str) -> tuple[bool, Optional[GitURLInfo]]:
    """
    解析 HTTPS URL

    支持格式：
    - https://github.com/user/repo
    - https://github.com/user/repo.git
    - https://github.com/user/repo/tree/main/commands
    """

    # 基础 URL 匹配
    pattern = r'^https?://([^/]+)/([^/]+)/([^/?]+)(\.git)?(/tree/([^/?]+))?(/(.*))?$'
    match = re.match(pattern, source)

    if not match:
        return False, None

    host, user, repo, _git_ext, _tree, branch, _slash, subpath = match.groups()

    # 提取子目录信息
    return True, GitURLInfo(
        protocol='https',
        host=host,
        user=user,
        repo=repo,
        branch=branch or 'main',  # 默认分支
        subpath=subpath or '',
        original_url=source
    )


def parse_ssh_url(source: str) -> tuple[bool, Optional[GitURLInfo]]:
    """
    解析 SSH URL

    支持格式：
    - git@github.com:user/repo.git
    - git@github.com:user/repo

    参考：https://labex.io/tutorials/git-how-to-validate-git-repository-url-434201
    """

    pattern = r'^git@([^:]+):([^/]+)/([^/?]+)(\.git)?$'
    match = re.match(pattern, source)

    if not match:
        return False, None

    host, user, repo = match.groups()[:3]

    return True, GitURLInfo(
        protocol='ssh',
        host=host,
        user=user,
        repo=repo,
        branch='main',  # SSH URL 通常不指定分支
        subpath='',
        original_url=source
    )


@dataclass
class GitURLInfo:
    """Git URL 解析结果"""
    protocol: str      # https, ssh, git
    host: str          # github.com, gitlab.com
    user: str          # 仓库所有者
    repo: str          # 仓库名称
    branch: str        # 分支名称
    subpath: str       # 子目录路径
    original_url: str  # 原始 URL
```

#### 子目录处理

对于包含子目录的 URL（如 `github.com/user/repo/tree/main/commands`），使用以下策略：

1. **克隆整个仓库**
2. **检出指定分支**
3. **切换到子目录**提取命令文件

```python
def extract_from_git_subdirectory(git_info: GitURLInfo, target_dir: Path) -> List[Path]:
    """
    从 Git 仓库的子目录中提取命令文件

    流程：
    1. git clone <url> --branch <branch> --depth 1 <temp_dir>
    2. cd <temp_dir>
    3. 复制 <subpath>/* 到 target_dir
    4. 删除临时目录
    """

    import tempfile
    import subprocess

    with tempfile.TemporaryDirectory() as temp_dir:
        # 克隆仓库
        clone_url = f"{git_info.protocol}://{git_info.host}/{git_info.user}/{git_info.repo}.git"
        subprocess.run([
            'git', 'clone',
            '--branch', git_info.branch,
            '--depth', '1',
            clone_url,
            temp_dir
        ], check=True)

        # 定位到子目录
        source_dir = Path(temp_dir) / git_info.subpath

        if not source_dir.exists():
            raise FileNotFoundError(f"子目录不存在：{git_info.subpath}")

        # 复制命令文件
        command_files = list(source_dir.glob('*.md'))
        for cmd_file in command_files:
            shutil.copy2(cmd_file, target_dir / cmd_file.name)

        return command_files
```

#### 平台特定 URL 特征

| 平台 | URL 特征 | 示例 |
|------|---------|------|
| **GitHub** | `github.com` + `/tree/` | `https://github.com/user/repo/tree/main/commands` |
| **GitLab** | `gitlab.com` + `/-/tree/` | `https://gitlab.com/user/repo/-/tree/main/commands` |
| **Bitbucket** | `bitbucket.org` + `/src/` | `https://bitbucket.org/user/repo/src/main/commands/` |

### 3.3 预设名称检测

#### 配置存储格式

根据功能规范中的配置文件设计：

```json
{
  "install_sources": {
    "presets": {
      "wiki-generator": "https://github.com/user/wiki-generator-repo",
      "code-reviewer": "https://github.com/team/code-reviewer",
      "test-helper": "./local-commands/test-helper"
    }
  }
}
```

#### 检测逻辑

```python
def is_preset_name(source: str, presets: Dict[str, str]) -> tuple[bool, Optional[str]]:
    """
    检测是否为预设命令名称

    规则：
    1. 完全匹配预设名称（区分大小写）
    2. 不包含路径分隔符 (/、\)
    3. 不包含 URL 特征字符（://、@）
    """

    # 规则 1: 完全匹配
    if source in presets:
        return True, presets[source]

    # 规则 2 & 3: 排除明显不是预设名称的输入
    if '/' in source or '\\' in source:
        return False, None
    if '://' in source or '@' in source:
        return False, None

    # 规则 4: 模糊匹配（可选项）
    # 支持简写形式，如 "wiki" 匹配 "wiki-generator"
    matches = [name for name in presets if name.startswith(source)]
    if len(matches) == 1:
        return True, presets[matches[0]]

    return False, None
```

#### 命名规范

**推荐命名约定**：
- 使用小写字母和连字符：`wiki-generator`、`code-reviewer`
- 避免使用下划线：不推荐 `wiki_generator`
- 使用描述性名称：`test-helper` 而非 `helper`
- 添加作用域前缀（可选）：`team/wiki-generator`（避免命名冲突）

**冲突处理**：
- **优先级**：本地配置 > 全局配置 > 内置预设
- **覆盖机制**：用户配置中的预设名称覆盖内置预设
- **冲突检测**：安装时检测并警告命名冲突

```python
def resolve_preset_conflict(preset_name: str, local_presets: Dict, global_presets: Dict) -> str:
    """
    解析预设名称冲突

    优先级：local > global > builtin
    """

    if preset_name in local_presets:
        return local_presets[preset_name]
    if preset_name in global_presets:
        return global_presets[preset_name]
    if preset_name in BUILTIN_PRESETS:
        return BUILTIN_PRESETS[preset_name]

    raise ValueError(f"未找到预设命令：{preset_name}")
```

---

## 4. URL 解析和验证

### 4.1 URL 格式验证

#### 验证流程

```python
def validate_git_url(source: str) -> tuple[bool, Optional[str]]:
    """
    验证 Git URL 有效性

    参考：
    - https://stackoverflow.com/questions/23976019/how-to-verify-valid-format-of-url-as-a-git-repo
    - https://www.geeksforgeeks.org/dsa/validate-git-repository-using-regular-expression/
    """

    # 步骤 1: 格式验证（正则表达式）
    if not is_valid_git_url_format(source):
        return False, "URL 格式无效"

    # 步骤 2: 协议验证
    protocol = extract_protocol(source)
    if protocol not in ['https', 'http', 'git', 'ssh']:
        return False, f"不支持的协议：{protocol}"

    # 步骤 3: 主机验证（可选）
    host = extract_host(source)
    if not is_valid_git_host(host):
        return False, f"未知的主机：{host}"

    # 步骤 4: 连接性验证（可选，耗时）
    if not check_git_repo_accessible(source):
        return False, "无法访问 Git 仓库"

    return True, None


def is_valid_git_url_format(source: str) -> bool:
    """
    正则表达式验证 Git URL 格式

    参考：https://www.geeksforgeeks.org/dsa/validate-git-repository-using-regular-expression/
    """

    # HTTPS/HTTP URL
    https_pattern = r'^https?://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}/[^/]+/[^/]+(\.git)?(/tree/[^/]+/.*)?$'

    # SSH URL
    ssh_pattern = r'^[a-zA-Z0-9\-\.]+@[a-zA-Z0-9\-\.]+:[^/]+/[^/]+(\.git)?$'

    # Git 协议
    git_pattern = r'^git://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}/[^/]+/[^/]+(\.git)?$'

    return bool(
        re.match(https_pattern, source) or
        re.match(ssh_pattern, source) or
        re.match(git_pattern, source)
    )


def check_git_repo_accessible(url: str, timeout: int = 10) -> bool:
    """
    检查 Git 仓库是否可访问

    方法：
    1. 尝试 git ls-remote（不克隆整个仓库）
    2. 超时控制
    """

    try:
        result = subprocess.run(
            ['git', 'ls-remote', url],
            capture_output=True,
            timeout=timeout,
            check=True
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return False
```

### 4.2 安全检查

#### URL 安全性验证

```python
def validate_url_security(source: str) -> tuple[bool, Optional[str]]:
    """
    URL 安全性检查

    参考：https://www.nodejs-security.com/blog/url-regex-validation
    """

    # 检查 1: 防止 SSRF 攻击（服务器端请求伪造）
    host = extract_host(source)
    if is_private_ip(host):
        return False, "不允许访问内网地址"

    # 检查 2: 防止重定向攻击
    if source.endswith('/..') or '../' in source:
        return False, "检测到路径遍历攻击"

    # 检查 3: 白名单主机（可选）
    if not is_whitelisted_host(host):
        return False, f"主机不在白名单中：{host}"

    # 检查 4: 协议限制
    protocol = extract_protocol(source)
    if protocol not in ['https', 'ssh']:
        return False, "仅支持 HTTPS 和 SSH 协议"

    return True, None


def is_private_ip(host: str) -> bool:
    """检查是否为内网 IP 或本地地址"""

    try:
        ip = socket.gethostbyname(host)
    except socket.gaierror:
        return False

    # 私有 IP 范围
    private_ranges = [
        ('10.0.0.0', '10.255.255.255'),
        ('172.16.0.0', '172.31.255.255'),
        ('192.168.0.0', '192.168.255.255'),
        ('127.0.0.0', '127.255.255.255'),  # 本地回环
    ]

    ip_int = int(ipaddress.ip_address(ip))

    for start, end in private_ranges:
        start_int = int(ipaddress.ip_address(start))
        end_int = int(ipaddress.ip_address(end))
        if start_int <= ip_int <= end_int:
            return True

    return False
```

### 4.3 平台特殊处理

#### GitHub URL 解析

```python
def parse_github_url(url: str) -> Optional[GitHubURLInfo]:
    """
    解析 GitHub URL

    参考：
    - https://regex101.com/library/uniQ2X
    - https://github.com/jonschlinkert/parse-github-url
    """

    # GitHub URL 正则表达式
    pattern = r'^https?://(?:www\.)?github\.com/([^/]+)/([^/]+)(?:/tree/([^/]+)(?:/(.*))?)?'

    match = re.match(pattern, url)
    if not match:
        return None

    owner, repo, branch, path = match.groups()

    return GitHubURLInfo(
        owner=owner,
        repo=repo.replace('.git', ''),  # 移除 .git 后缀
        branch=branch or 'main',
        path=path or '',
        original_url=url
    )
```

#### GitLab URL 解析

```python
def parse_gitlab_url(url: str) -> Optional[GitLabURLInfo]:
    """
    解析 GitLab URL

    GitLab 特征：
    - 使用 /-/tree/ 而非 /tree/
    - 支持嵌套命名空间（group/subgroup/project）
    """

    # GitLab URL 正则表达式
    pattern = r'^https?://(?:www\.)?gitlab\.com/([^/]+(?:/[^/]+)*?)/([^/]+)(?:/-/tree/([^/]+)(?:/(.*))?)?'

    match = re.match(pattern, url)
    if not match:
        return None

    namespace, project, branch, path = match.groups()

    return GitLabURLInfo(
        namespace=namespace,
        project=project.replace('.git', ''),
        branch=branch or 'main',
        path=path or '',
        original_url=url
    )
```

---

## 5. 本地路径解析

### 5.1 路径规范化

```python
def normalize_local_path(source: str, base_dir: Path) -> Path:
    """
    规范化本地路径

    处理：
    1. 相对路径展开
    2. ~ 符号展开
    3. 符号链接解析
    4. 路径规范化（消除 ../ 和 ./）
    """

    # 展开波浪号
    if source.startswith('~'):
        path = Path(source).expanduser()
    else:
        path = Path(source)

    # 相对路径 → 绝对路径
    if not path.is_absolute():
        path = (base_dir / path).resolve()

    # 解析符号链接
    try:
        path = path.resolve()
    except OSError:
        # 符号链接损坏，保留原始路径
        pass

    return path
```

### 5.2 存在性和可读性验证

```python
def validate_local_path(path: Path) -> tuple[bool, Optional[str]]:
    """
    验证本地路径的有效性

    检查：
    1. 路径是否存在
    2. 是否可读
    3. 是否为文件或目录
    """

    # 检查 1: 路径存在性
    if not path.exists():
        return False, f"路径不存在：{path}"

    # 检查 2: 可读性
    if not os.access(path, os.R_OK):
        return False, f"无读取权限：{path}"

    # 检查 3: 文件类型
    if path.is_file():
        if not is_markdown_file(path):
            return False, f"不是 Markdown 文件：{path}"
    elif path.is_dir():
        if not list(path.glob('*.md')):
            return False, f"目录中未找到 Markdown 文件：{path}"
    else:
        return False, f"不支持的文件类型：{path}"

    return True, None


def is_markdown_file(path: Path) -> bool:
    """检查是否为 Markdown 文件"""
    return path.suffix.lower() in ['.md', '.markdown']
```

### 5.3 文件 vs 目录处理

```python
def extract_from_local_path(path: Path) -> List[Path]:
    """
    从本地路径提取命令文件

    策略：
    1. 文件 → 直接使用
    2. 目录 → 扫描所有 .md 文件
    """

    if path.is_file():
        # 单个文件
        return [path]

    elif path.is_dir():
        # 目录：扫描所有 Markdown 文件
        command_files = list(path.glob('*.md'))
        command_files.extend(list(path.glob('**/*.md')))  # 递归扫描

        return command_files

    else:
        raise ValueError(f"无效的路径类型：{path}")
```

### 5.4 符号链接处理

```python
def handle_symlinks(path: Path) -> Path:
    """
    处理符号链接

    策略：
    1. 解析符号链接到实际路径
    2. 检查循环引用
    3. 限制解析深度
    """

    max_depth = 10
    current_depth = 0
    visited = set()

    while path.is_symlink() and current_depth < max_depth:
        # 检查循环引用
        real_path = path.resolve()
        if str(real_path) in visited:
            raise ValueError(f"检测到循环符号链接：{path}")

        visited.add(str(real_path))
        path = real_path
        current_depth += 1

    if current_depth >= max_depth:
        raise ValueError(f"符号链接解析深度超过限制：{path}")

    return path
```

---

## 6. 预设名称映射

### 6.1 配置文件结构

```json
{
  "install_sources": {
    "presets": {
      "wiki-generator": {
        "url": "https://github.com/user/wiki-generator-repo",
        "description": "Wiki 文档生成器",
        "version": "1.0.0",
        "author": "Repo Wiki Generator Team",
        "homepage": "https://github.com/user/wiki-generator-repo",
        "last_updated": "2025-01-03T08:00:00Z"
      },
      "code-reviewer": {
        "url": "./local-commands/code-reviewer",
        "description": "代码审查助手",
        "version": "2.1.0"
      }
    },
    "builtin_presets": {
      "wiki-generator": "https://github.com/user/wiki-generator-repo",
      "test-helper": "https://github.com/team/test-helper"
    }
  },
  "settings": {
    "preset_auto_update": false,
    "preset_update_interval": 86400
  }
}
```

### 6.2 预设解析逻辑

```python
def resolve_preset_source(preset_name: str, config: Dict) -> tuple[bool, Optional[str]]:
    """
    解析预设命令名称到实际来源

    优先级：
    1. 用户自定义预设（.claude/command-install.json）
    2. 全局配置（~/.claude/command-install.json）
    3. 内置预设（hardcoded）
    """

    # 优先级 1: 用户本地配置
    local_presets = config.get('install_sources', {}).get('presets', {})
    if preset_name in local_presets:
        preset_info = local_presets[preset_name]
        # 支持简写字符串或完整对象
        url = preset_info if isinstance(preset_info, str) else preset_info.get('url')
        return True, url

    # 优先级 2: 全局配置
    global_config = load_global_config()
    global_presets = global_config.get('install_sources', {}).get('presets', {})
    if preset_name in global_presets:
        return True, global_presets[preset_name].get('url')

    # 优先级 3: 内置预设
    if preset_name in BUILTIN_PRESETS:
        return True, BUILTIN_PRESETS[preset_name]

    return False, None


BUILTIN_PRESETS = {
    "wiki-generator": "https://github.com/user/wiki-generator-repo",
    "test-helper": "https://github.com/team/test-helper",
    # 更多内置预设...
}
```

### 6.3 预设更新机制

```python
def update_preset_sources(config_path: Path, force: bool = False) -> Dict:
    """
    更新预设来源配置

    策略：
    1. 检查最后更新时间
    2. 从远程获取最新预设列表
    3. 合并本地和远程配置
    """

    config = load_config(config_path)
    settings = config.get('settings', {})

    # 检查是否需要更新
    if not force and not should_update_presets(settings):
        return config

    # 从远程获取最新预设（示例：从 JSON 配置仓库）
    remote_presets = fetch_remote_presets()

    # 合并配置
    local_presets = config.get('install_sources', {}).get('presets', {})
    merged_presets = {**remote_presets, **local_presets}  # 本地覆盖远程

    config['install_sources']['presets'] = merged_presets
    config['install_sources']['last_updated'] = datetime.now().isoformat()

    # 保存配置
    save_config(config_path, config)

    return config


def should_update_presets(settings: Dict) -> bool:
    """检查是否需要更新预设"""

    auto_update = settings.get('preset_auto_update', False)
    if not auto_update:
        return False

    interval = settings.get('preset_update_interval', 86400)  # 默认 24 小时
    last_updated = settings.get('preset_last_updated', 0)

    return (time.time() - last_updated) > interval
```

---

## 7. 错误处理

### 7.1 错误分类

```python
class SourceResolutionError(Exception):
    """来源解析错误基类"""
    pass


class InvalidSourceFormatError(SourceResolutionError):
    """无效的来源格式"""
    pass


class LocalPathNotFoundError(SourceResolutionError):
    """本地路径不存在"""
    pass


class GitURLAccessError(SourceResolutionError):
    """Git URL 无法访问"""
    pass


class PresetNotFoundError(SourceResolutionError):
    """预设名称未找到"""
    pass


class SecurityValidationError(SourceResolutionError):
    """安全验证失败"""
    pass
```

### 7.2 友好错误消息

```python
def format_error_message(error: Exception, source: str) -> str:
    """
    生成用户友好的错误消息

    原则：
    1. 明确指出问题
    2. 提供具体原因
    3. 给出解决建议
    """

    if isinstance(error, InvalidSourceFormatError):
        return f"""
❌ 无效的命令来源格式：{source}

💡 可能的原因：
  • URL 格式不正确
  • 本地路径不存在
  • 预设名称拼写错误

🔗 帮助：
  • Git URL 示例：https://github.com/user/repo
  • 本地路径示例：./commands/my-command.md
  • 预设名称示例：wiki-generator

使用 /command.install help 查看详细帮助
"""

    elif isinstance(error, LocalPathNotFoundError):
        return f"""
❌ 本地路径不存在：{source}

💡 建议：
  • 检查路径拼写是否正确
  • 使用绝对路径或相对于项目根目录的路径
  • 确认文件确实存在

当前目录：{os.getcwd()}
"""

    elif isinstance(error, GitURLAccessError):
        return f"""
❌ 无法访问 Git 仓库：{source}

💡 可能的原因：
  • 仓库不存在或 URL 错误
  • 网络连接问题
  • 权限不足（私有仓库）

🔗 建议：
  • 在浏览器中验证 URL 是否可访问
  • 检查网络连接
  • 如果是私有仓库，确保已配置 SSH 密钥或访问令牌
"""

    elif isinstance(error, PresetNotFoundError):
        return f"""
❌ 未找到预设命令：{source}

💡 建议：
  • 检查预设名称拼写
  • 使用 /command.install list-presets 查看所有可用预设
  • 使用完整 URL 或本地路径替代

可用预设：{', '.join(get_available_preset_names())}
"""

    elif isinstance(error, SecurityValidationError):
        return f"""
❌ 安全验证失败：{source}

⚠️  检测到潜在安全风险：
  • {str(error)}

💡 建议：
  • 仅安装来自可信来源的命令
  • 避免使用内网 IP 或本地文件 URL
  • 使用 HTTPS 协议而非 HTTP
"""

    else:
        return f"""
❌ 未知错误：{str(error)}

🔗 帮助：
  使用 /command.install help 查看使用说明
  或提交 issue：https://github.com/user/repo/issues
"""
```

### 7.3 降级策略

```python
def resolve_source_with_fallback(source: str, config: Dict) -> tuple[str, str]:
    """
    带降级策略的来源解析

    降级流程：
    1. 尝试完整解析
    2. 如果失败，尝试替代方案
    3. 如果仍然失败，返回错误
    """

    try:
        # 尝试 1: 标准解析
        return resolve_source(source, config)
    except GitURLAccessError as e:
        # 降级策略 1: 尝试使用 SSH 替代 HTTPS
        if source.startswith('https://'):
            ssh_url = convert_https_to_ssh(source)
            try:
                test_git_access(ssh_url)
                return ssh_url, 'ssh'
            except:
                pass

        # 降级策略 2: 尝试从镜像克隆
        mirror_url = get_mirror_url(source)
        if mirror_url:
            try:
                test_git_access(mirror_url)
                return mirror_url, 'mirror'
            except:
                pass

        # 所有降级策略失败
        raise e

    except PresetNotFoundError as e:
        # 降级策略: 搜索相似的预设名称
        similar_presets = find_similar_preset_names(source, config)
        if similar_presets:
            suggestion = similar_presets[0]
            raise PresetNotFoundError(
                f"未找到预设 '{source}'，您是指 '{suggestion}' 吗？"
            )
        raise e


def convert_https_to_ssh(https_url: str) -> str:
    """将 HTTPS URL 转换为 SSH URL"""
    # https://github.com/user/repo.git → git@github.com:user/repo.git
    match = re.match(r'^https?://([^/]+)/([^/]+)/([^/]+)(\.git)?$', https_url)
    if match:
        host, user, repo, _git = match.groups()
        return f"git@{host}:{user}/{repo}.git"
    return https_url
```

---

## 8. 完整解析流程

### 8.1 主解析器

```python
def resolve_command_source(source: str, config: Dict) -> SourceInfo:
    """
    命令来源解析器（主入口）

    参数：
        source: 用户输入的来源字符串
        config: 配置字典

    返回：
        SourceInfo: 解析后的来源信息

    抛出：
        SourceResolutionError: 解析失败
    """

    # 步骤 1: 本地路径检测（最高优先级）
    if is_local_path(source):
        normalized_path = normalize_local_path(source, get_cwd())
        valid, error = validate_local_path(normalized_path)
        if not valid:
            raise LocalPathNotFoundError(error)

        return SourceInfo(
            type='local',
            path=str(normalized_path),
            original=source
        )

    # 步骤 2: Git URL 检测
    is_url, url_info = is_git_url(source)
    if is_url:
        valid, error = validate_git_url(source)
        if not valid:
            raise GitURLAccessError(error)

        valid, error = validate_url_security(source)
        if not valid:
            raise SecurityValidationError(error)

        return SourceInfo(
            type='git',
            url=url_info.original_url,
            protocol=url_info.protocol,
            host=url_info.host,
            branch=url_info.branch,
            subpath=url_info.subpath,
            original=source
        )

    # 步骤 3: 预设名称检测（最低优先级）
    is_preset, preset_url = is_preset_name(source, config.get('install_sources', {}).get('presets', {}))
    if is_preset:
        # 递归解析预设 URL（可能也是本地路径或 Git URL）
        return resolve_command_source(preset_url, config)

    # 步骤 4: 无法识别的来源
    raise InvalidSourceFormatError(f"无法识别的命令来源：{source}")


@dataclass
class SourceInfo:
    """来源信息"""
    type: str              # 'local', 'git', 'preset'
    original: str          # 原始输入
    path: Optional[str] = None       # 本地路径（type='local'）
    url: Optional[str] = None        # Git URL（type='git'）
    protocol: Optional[str] = None   # Git 协议（type='git'）
    host: Optional[str] = None       # Git 主机（type='git'）
    branch: Optional[str] = None     # Git 分支（type='git'）
    subpath: Optional[str] = None    # Git 子目录（type='git'）
```

### 8.2 流程图

```
用户输入来源
    ↓
┌───────────────────────────────┐
│  步骤 1: 本地路径检测          │
│  - 检查 ./、../、/、~ 等前缀   │
│  - 检查路径是否存在            │
└───────────┬───────────────────┘
            │
      是本地路径？
      ↓ Yes      ↓ No
   返回 LocalInfo  继续
                      ↓
┌───────────────────────────────┐
│  步骤 2: Git URL 检测          │
│  - HTTPS/SSH/Git 协议检测      │
│  - URL 格式验证               │
│  - 安全性检查                 │
└───────────┬───────────────────┘
            │
      是 Git URL？
      ↓ Yes      ↓ No
   �返回 GitInfo   继续
                      ↓
┌───────────────────────────────┐
│  步骤 3: 预设名称检测          │
│  - 匹配预设配置               │
│  - 递归解析预设 URL            │
└───────────┬───────────────────┘
            │
      是预设名称？
      ↓ Yes      ↓ No
   递归解析    抛出错误
```

---

## 9. 边界情况清单

### 9.1 本地路径边界情况

| # | 输入场景 | 预期行为 | 实现要点 |
|---|---------|---------|---------|
| 1 | 空字符串 | 抛出错误 | 检测空输入 |
| 2 | `.`（当前目录） | 扫描当前目录 | 展开为绝对路径 |
| 3 | `..`（父目录） | 扫描父目录 | 展开为绝对路径 |
| 4 | `~`（home 目录） | 展开为 home | 使用 `Path.expanduser()` |
| 5 | 相对路径嵌套 `../../cmd` | 正确解析 | 使用 `Path.resolve()` |
| 6 | 符号链接 | 解析到实际路径 | 限制解析深度 |
| 7 | 循环符号链接 | 检测并报错 | 维护访问记录 |
| 8 | 路径包含空格 | 正确处理 | 使用引号或转义 |
| 9 | 路径不存在 | 友好错误 | 提供建议 |
| 10 | 无读取权限 | 友好错误 | 检查 `os.R_OK` |

### 9.2 Git URL 边界情况

| # | 输入场景 | 预期行为 | 实现要点 |
|---|---------|---------|---------|
| 1 | 无效的 URL 格式 | 抛出错误 | 正则验证 |
| 2 | 仓库不存在 | 友好错误 | `git ls-remote` 检测 |
| 3 | 私有仓库（无权限） | 友好错误 | 检测 403/401 |
| 4 | 子目录不存在 | 抛出错误 | 克隆后检查路径 |
| 5 | 分支不存在 | 友好错误 | 列出可用分支 |
| 6 | 带 `.git` 后缀 | 正确处理 | 移除或保留 |
| 7 | 不带 `.git` 后缀 | 正确处理 | 自动添加 |
| 8 | URL 包含查询参数 | 忽略参数 | 解析时过滤 |
| 9 | URL 包含锚点 | 忽略锚点 | 解析时过滤 |
| 10 | 内网 IP 地址 | 安全警告 | SSRF 防护 |
| 11 | HTTP（非 HTTPS） | 安全警告 | 推荐使用 HTTPS |
| 12 | GitLab 子组路径 | 正确解析 | 嵌套命名空间 |

### 9.3 预设名称边界情况

| # | 输入场景 | 预期行为 | 实现要点 |
|---|---------|---------|---------|
| 1 | 预设名称不存在 | 抛出错误 | 提供相似名称建议 |
| 2 | 预设名称冲突 | 使用优先级 | 本地 > 全局 > 内置 |
| 3 | 预设指向无效 URL | 抛出错误 | 递归验证 |
| 4 | 预设指向本地路径 | 递归解析 | 支持本地预设 |
| 5 | 预设名称大小写 | 区分大小写 | 精确匹配 |
| 6 | 预设名称包含空格 | 报错 | 不允许空格 |
| 7 | 预设名称为空 | 报错 | 检测空字符串 |
| 8 | 预设 URL 循环引用 | 检测并报错 | 维护访问栈 |
| 9 | 预设 URL 过期 | 更新机制 | 定期刷新 |
| 10 | 内置预设被覆盖 | 警告用户 | 明确提示 |

### 9.4 复合边界情况

| # | 输入场景 | 预期行为 | 实现要点 |
|---|---------|---------|---------|
| 1 | 预设名称与本地路径同名 | 本地路径优先 | 检测优先级 |
| 2 | URL 看起来像预设名 | URL 优先 | `://` 特征检测 |
| 3 | 相对路径 `./github.com` | 本地路径 | 非域名检测 |
| 4 | `git@` 作为文件名 | Git URL | 协议标记优先 |
| 5 | Windows 路径 `C:\repo` | 本地路径 | 盘符检测 |
| 6 | 特殊字符 `../` | 本地路径 | 路径遍历检测 |
| 7 | Unicode 路径 | 正确处理 | 使用 `Path` 而非字符串 |

---

## 10. 测试场景

### 10.1 单元测试用例

```python
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

class TestSourceResolution:

    # 本地路径测试
    def test_relative_path_with_dot_slash(self):
        """测试 ./ 前缀的相对路径"""
        source = "./commands/my-command.md"
        info = resolve_command_source(source, {})
        assert info.type == 'local'
        assert info.original == source

    def test_relative_path_with_double_dot(self):
        """测试 ../ 前缀的父目录路径"""
        source = "../shared-commands/common.md"
        info = resolve_command_source(source, {})
        assert info.type == 'local'

    def test_absolute_path_unix(self):
        """测试 Unix 绝对路径"""
        source = "/home/user/commands/command.md"
        info = resolve_command_source(source, {})
        assert info.type == 'local'

    def test_absolute_path_windows(self):
        """测试 Windows 绝对路径"""
        source = "C:\\commands\\my-command.md"
        info = resolve_command_source(source, {})
        assert info.type == 'local'

    def test_home_directory_expansion(self):
        """测试 ~ 符号展开"""
        source = "~/commands/my-command.md"
        info = resolve_command_source(source, {})
        assert info.type == 'local'
        assert info.path.startswith(str(Path.home()))

    def test_nonexistent_local_path(self):
        """测试不存在的本地路径"""
        source = "./nonexistent/command.md"
        with pytest.raises(LocalPathNotFoundError):
            resolve_command_source(source, {})

    # Git URL 测试
    def test_github_https_url(self):
        """测试 GitHub HTTPS URL"""
        source = "https://github.com/user/repo"
        info = resolve_command_source(source, {})
        assert info.type == 'git'
        assert info.protocol == 'https'
        assert info.host == 'github.com'
        assert info.branch == 'main'

    def test_github_ssh_url(self):
        """测试 GitHub SSH URL"""
        source = "git@github.com:user/repo.git"
        info = resolve_command_source(source, {})
        assert info.type == 'git'
        assert info.protocol == 'ssh'
        assert info.host == 'github.com'

    def test_github_url_with_subdirectory(self):
        """测试带子目录的 GitHub URL"""
        source = "https://github.com/user/repo/tree/main/commands"
        info = resolve_command_source(source, {})
        assert info.type == 'git'
        assert info.subpath == 'commands'
        assert info.branch == 'main'

    def test_gitlab_url(self):
        """测试 GitLab URL"""
        source = "https://gitlab.com/user/repo"
        info = resolve_command_source(source, {})
        assert info.type == 'git'
        assert info.host == 'gitlab.com'

    def test_invalid_git_url(self):
        """测试无效的 Git URL"""
        source = "https://invalid-url-format"
        with pytest.raises(InvalidSourceFormatError):
            resolve_command_source(source, {})

    # 预设名称测试
    def test_valid_preset_name(self):
        """测试有效的预设名称"""
        source = "wiki-generator"
        config = {
            'install_sources': {
                'presets': {
                    'wiki-generator': 'https://github.com/user/repo'
                }
            }
        }
        info = resolve_command_source(source, config)
        assert info.type == 'git'
        assert info.url == 'https://github.com/user/repo'

    def test_preset_name_not_found(self):
        """测试不存在的预设名称"""
        source = "nonexistent-preset"
        with pytest.raises(PresetNotFoundError):
            resolve_command_source(source, {})

    def test_preset_name_to_local_path(self):
        """测试预设名称映射到本地路径"""
        source = "local-helper"
        config = {
            'install_sources': {
                'presets': {
                    'local-helper': './local-commands/helper.md'
                }
            }
        }
        info = resolve_command_source(source, config)
        assert info.type == 'local'

    # 边界情况测试
    def test_empty_string(self):
        """测试空字符串"""
        source = ""
        with pytest.raises(InvalidSourceFormatError):
            resolve_command_source(source, {})

    def test_url_looks_like_preset(self):
        """测试看起来像预设名的 URL"""
        source = "https://github.com"
        info = resolve_command_source(source, {})
        assert info.type == 'git'

    def test_local_path_with_url_characters(self):
        """测试包含 URL 字符的本地路径"""
        source = "./github.com-backup/command.md"
        info = resolve_command_source(source, {})
        assert info.type == 'local'
```

### 10.2 集成测试场景

```python
class TestSourceResolutionIntegration:

    def test_install_from_github_subdirectory(self, tmp_path):
        """测试从 GitHub 子目录安装"""
        source = "https://github.com/test/repo/tree/main/commands"
        info = resolve_command_source(source, {})

        # 模拟克隆和提取
        with TemporaryDirectory() as temp_dir:
            files = extract_from_git_subdirectory(info.git_info, tmp_path)
            assert len(files) > 0
            assert all(f.suffix == '.md' for f in files)

    def test_install_from_local_directory(self, tmp_path):
        """测试从本地目录安装"""
        # 创建测试目录
        source_dir = tmp_path / 'commands'
        source_dir.mkdir()
        (source_dir / 'command1.md').write_text('# Command 1')
        (source_dir / 'command2.md').write_text('# Command 2')

        info = resolve_command_source(str(source_dir), {})
        assert info.type == 'local'

        files = extract_from_local_path(Path(info.path))
        assert len(files) == 2

    def test_preset_resolution_chain(self, tmp_path):
        """测试预设名称解析链"""
        config = {
            'install_sources': {
                'presets': {
                    'wiki': 'https://github.com/user/wiki-repo',
                    'wiki-extended': 'wiki'  # 预设引用另一个预设
                }
            }
        }

        info = resolve_command_source('wiki-extended', config)
        assert info.type == 'git'
        assert info.url == 'https://github.com/user/wiki-repo'

    def test_error_recovery_with_suggestions(self, tmp_path):
        """测试错误恢复和建议"""
        config = {
            'install_sources': {
                'presets': {
                    'wiki-generator': 'https://github.com/user/repo'
                }
            }
        }

        with pytest.raises(PresetNotFoundError) as exc_info:
            resolve_command_source('wiki-genrator', config)  # 拼写错误

        # 验证错误消息包含建议
        error_msg = str(exc_info.value)
        assert 'wiki-generator' in error_msg
```

### 10.3 性能测试

```python
class TestSourceResolutionPerformance:

    def test_local_path_resolution_speed(self):
        """测试本地路径解析速度"""
        import time

        source = './commands/my-command.md'
        start = time.time()
        for _ in range(1000):
            resolve_command_source(source, {})
        duration = time.time() - start

        assert duration < 0.1  # 1000 次解析应在 100ms 内完成

    def test_git_url_validation_speed(self):
        """测试 Git URL 验证速度"""
        source = 'https://github.com/user/repo'
        start = time.time()
        for _ in range(1000):
            is_git_url(source)
        duration = time.time() - start

        assert duration < 0.05  # 正则匹配应非常快

    def test_preset_resolution_speed(self):
        """测试预设解析速度"""
        config = {
            'install_sources': {
                'presets': {f'preset-{i}': f'https://github.com/user/repo{i}' for i in range(100)}
            }
        }

        start = time.time()
        for i in range(100):
            resolve_command_source(f'preset-{i}', config)
        duration = time.time() - start

        assert duration < 0.1  # 字典查找应非常快
```

---

## 11. 实现建议

### 11.1 关键设计决策

| 决策点 | 推荐方案 | 理由 |
|-------|---------|------|
| **检测顺序** | 本地路径 > Git URL > 预设名称 | 避免误识别，明确优先级 |
| **路径解析** | 使用 `pathlib.Path` 而非字符串 | 跨平台兼容，自动处理分隔符 |
| **URL 解析** | 正则表达式 + 手动解析 | Git URL 格式特殊，标准 URL 解析器不支持 |
| **符号链接** | 解析到实际路径，限制深度 | 避免循环引用 |
| **安全检查** | 白名单主机 + SSRF 防护 | 防止内网访问和重定向攻击 |
| **错误处理** | 分层异常 + 友好消息 | 提供明确的解决建议 |
| **配置存储** | JSON 格式，支持嵌套对象 | 易于编辑，支持扩展字段 |
| **预设更新** | 定期检查，手动强制更新 | 平衡及时性和性能 |

### 11.2 实现优先级

**阶段 1：核心功能（MVP）**
1. 本地路径解析（相对/绝对路径）
2. Git HTTPS URL 解析
3. 基础预设名称映射

**阶段 2：增强功能**
1. Git SSH URL 解析
2. 子目录处理
3. 符号链接处理
4. 错误消息优化

**阶段 3：高级功能**
1. GitLab/Bitbucket URL 解析
2. 安全检查（SSRF 防护）
3. 预设自动更新
4. 性能优化

### 11.3 依赖库推荐

```python
# 推荐使用的标准库
from pathlib import Path          # 路径处理
from dataclasses import dataclass # 数据类
from typing import Dict, List, Optional, Tuple  # 类型注解
import re                         # 正则表达式
import os                         # 系统操作
import subprocess                 # Git 命令执行
import tempfile                   # 临时目录
import shutil                     # 文件操作
import socket                     # 网络检查
import ipaddress                  # IP 地址验证

# 可选的第三方库
# import requests                  # HTTP 请求（可选）
# import git                       # GitPython（可选，用于高级 Git 操作）
# import pydantic                  # 数据验证（可选）
```

### 11.4 代码组织建议

```
command_install/
├── __init__.py
├── resolver/
│   ├── __init__.py
│   ├── base.py          # 基础类和异常定义
│   ├── local.py         # 本地路径解析
│   ├── git.py           # Git URL 解析
│   ├── preset.py        # 预设名称解析
│   └── main.py          # 主解析器入口
├── validators/
│   ├── __init__.py
│   ├── url.py           # URL 验证
│   ├── security.py      # 安全检查
│   └── path.py          # 路径验证
├── extractors/
│   ├── __init__.py
│   ├── git_extractor.py # Git 仓库文件提取
│   └── local_extractor.py # 本地文件提取
└── utils/
    ├── __init__.py
    ├── config.py        # 配置管理
    └── errors.py        # 错误处理
```

---

## 12. 参考资料

### 12.1 研究来源

1. **Git URL 解析**
   - [StackOverflow: How to verify valid format of URL as a git repo?](https://stackoverflow.com/questions/23976019/how-to-verify-valid-format-of-url-as-a-git-repo)
   - [LabEx: How to validate git repository url](https://labex.io/tutorials/git-how-to-validate-git-repository-url-434201)
   - [GeeksforGeeks: Validate GIT Repository using Regular Expression](https://www.geeksforgeeks.org/dsa/validate-git-repository-using-regular-expression/)
   - [Node.js Issue: Support parsing url with ssh protocol](https://github.com/nodejs/node/issues/36172)

2. **URI/URL 规范**
   - [RFC 3986: Uniform Resource Identifier (URI): Generic Syntax](https://www.rfc-editor.org/rfc/rfc3986.html)
   - [RFC 8089: The "file" URI Scheme](https://datatracker.ietf.org/doc/rfc8089/)
   - [StackOverflow: Difference Between URL, URI, Path](https://stackoverflow.com/questions/27845223/whats-the-difference-between-a-resource-uri-url-path-and-file-in-java)

3. **URL 安全**
   - [Node.js Security: URL Regex Validation](https://www.nodejs-security.com/blog/url-regex-validation)
   - [ResearchGate: Detecting Malicious URLs Using Lexical Analysis](https://www.researchgate.net/publication/308365207_Detecting_Malicious_URLs_Using_Lexical_Analysis)

4. **GitHub URL 解析**
   - [Regex101: GitHub URL Parser](https://regex101.com/library/uniQ2X)
   - [GitHub: parse-github-url](https://github.com/jonschlinkert/parse-github-url)
   - [StackOverflow: Persistent URL for GitHub repo subfolder](https://stackoverflow.com/questions/71320429/persistent-url-for-github-repo-subfolder)

5. **包管理器最佳实践**
   - [Snyk: Modern npm Package Security Best Practices (2025)](https://snyk.io/blog/best-practices-create-modern-npm-package/)
   - [Homebrew Formula Cookbook](https://docs.brew.sh/Formula-Cookbook)
   - [npm: package.json Documentation](https://docs.npmjs.com/files/package.json/)

6. **Git 文档**
   - [Git Documentation: git-config](https://git-scm.com/docs/git-config)
   - [Git SCM: Git URLs](https://git-scm.com/docs/git-clone#_git_urls)

---

## 13. 总结

### 13.1 核心要点

1. **分层检测策略**：本地路径 > Git URL > 预设名称，确保优先级清晰
2. **健壮的验证**：格式验证 + 连接性验证 + 安全检查
3. **友好的错误处理**：明确的问题描述 + 具体的解决建议
4. **全面的边界情况**：考虑各种特殊输入和极端场景
5. **性能优化**：正则表达式快速匹配，字典查找 O(1) 复杂度

### 13.2 实现路线图

**第 1 周**：核心解析器
- 实现本地路径解析
- 实现 Git HTTPS URL 解析
- 实现基础预设映射

**第 2 周**：增强功能
- 添加 SSH URL 支持
- 实现子目录处理
- 优化错误消息

**第 3 周**：高级特性
- 添加安全检查
- 实现预设自动更新
- 性能优化和测试

### 13.3 成功指标

- ✅ 支持所有 3 种来源类型
- ✅ 覆盖 90%+ 的边界情况
- ✅ 单元测试覆盖率 ≥ 95%
- ✅ 解析速度 < 10ms（本地），< 100ms（Git URL）
- ✅ 用户能根据错误消息自行解决问题

---

**文档状态**: ✅ 研究完成
**下一步**: 基于本报告实现命令来源解析器
**创建日期**: 2025-01-03
**作者**: Claude Code 研究团队
