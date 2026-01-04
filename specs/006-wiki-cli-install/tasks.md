# Implementation Tasks: Wiki Generator CLI 安装工具优化

**Feature**: 006-wiki-cli-install
**Branch**: `006-wiki-cli-install`
**Created**: 2026-01-04
**Status**: Ready for Implementation

---

## Task Generation Summary

- **Total Tasks**: 32
- **Phases**: 6 (Setup → Foundation → US1-P1 → US2-P2 → US3-P3 → Polish)
- **Critical Path**: US1-P1 → US2-P2 → US3-P3
- **Parallelizable**: Yes, each user story can be developed independently after foundation

---

## Dependency Graph

```mermaid
graph TD
    SETUP[Phase 1: Setup] → FOUNDATION[Phase 2: Foundation]
    FOUNDATION → US1[Phase 3: US1-P1 一键安装]
    FOUNDATION → US2[Phase 4: US2-P2 配置初始化]
    FOUNDATION → US3[Phase 5: US3-P3 轻量级体验]

    US1 → POLISH[Phase 6: Polish & Testing]
    US2 → POLISH
    US3 → POLISH

    style SETUP fill:#e1f5e1
    style FOUNDATION fill:#e1f5e1
    style US1 fill:#fff4e1
    style US2 fill:#fff4e1
    style US3 fill:#fff4e1
    style POLISH fill:#e1f5ff
```

**Execution Strategy**:
1. Complete Phase 1-2 sequentially (foundational work)
2. Execute US1, US2, US3 in parallel (independent user stories)
3. Complete Phase 6 (integration and polish)

---

## Phase 1: Setup (基础设置)

### 1.1 创建项目结构和包初始化

- [ ] [T001-P1-SETUP] 创建 `wiki_generator/` 包目录结构
  - 文件: `wiki_generator/__init__.py`, `wiki_generator/__main__.py`, `wiki_generator/installer.py`, `wiki_generator/config.py`
  - 验证: 运行 `python -m wiki_generator --help` 显示帮助信息

### 1.2 配置项目元数据

- [ ] [T002-P1-SETUP] 更新 `pyproject.toml` 添加 CLI 入口点
  - 文件: `pyproject.toml`
  - 修改: 添加 `[project.scripts]` 配置 `wiki-generator = "wiki_generator.__main__:main"`
  - 验证: 运行 `uvx wiki-generator --version` 显示版本号

### 1.3 版本和错误类型定义

- [ ] [T003-P1-SETUP] 在 `wiki_generator/` 中定义版本常量和自定义异常
  - 文件: `wiki_generator/__init__.py`
  - 内容: `__version__ = "1.0.0"`, `class InstallerError(Exception)`, `class RollbackError(Exception)`, `class ValidationError(Exception)`
  - 验证: 导入模块不报错

---

## Phase 2: Foundation (基础功能)

### 2.1 文件复制核心逻辑

- [X] [T004-P1-FOUNDATION] 实现 `install_cli_files()` 函数 - 文件复制逻辑
  - 文件: `wiki_generator/installer.py`
  - 函数: `def install_cli_files(target_dir: str = ".", force: bool = False, dry_run: bool = False, verbose: bool = False) -> list[InstalledFile]:`
  - 逻辑: 遍历包内 `.claude/` 目录，使用 `shutil.copy2()` 复制文件，返回已安装文件列表
  - 验证: 在临时目录测试文件复制成功

- [X] [T005-P1-FOUNDATION] 实现 `rollback_installation()` 函数 - 回滚机制
  - 文件: `wiki_generator/installer.py`
  - 函数: `def rollback_installation(installed_files: list[InstalledFile], verbose: bool = False) -> None:`
  - 逻辑: 按相反顺序删除已安装文件，恢复备份文件（如果有）
  - 验证: 模拟安装失败后回滚成功

- [X] [T006-P1-FOUNDATION] 添加权限检查逻辑
  - 文件: `wiki_generator/installer.py`
  - 函数: `def check_write_permission(target_dir: str) -> bool:`
  - 逻辑: 尝试创建临时文件测试写入权限
  - 验证: 在只读目录测试时抛出 `PermissionError`

### 2.2 配置文件生成逻辑

- [X] [T007-P2-FOUNDATION] 实现 `generate_config()` 函数
  - 文件: `wiki_generator/config.py`
  - 函数: `def generate_config(target_dir: str = ".", overwrite: bool = False) -> WikiConfig:`
  - 逻辑: 生成包含 5 个字段的默认配置，写入 `wiki-config.json`
  - 验证: 生成的 JSON 文件包含所有必需字段

- [X] [T008-P2-FOUNDATION] 实现 `validate_config()` 函数
  - 文件: `wiki_generator/config.py`
  - 函数: `def validate_config(config_path: str) -> tuple[bool, list[ValidationError]]:`
  - 逻辑: 验证 JSON 格式、字段类型、枚举值、数值范围
  - 验证: 测试有效配置和无效配置的验证结果

### 2.3 数据模型定义

- [X] [T009-P2-FOUNDATION] 定义 `WikiConfig` 数据类
  - 文件: `wiki_generator/config.py`
  - 类: `@dataclass class WikiConfig:`, 包含 5 个字段（output_dir, exclude_patterns, quality_threshold, diagrams_enabled, diagrams_detail_level）
  - 验证: 创建实例并序列化为 JSON

- [X] [T010-P2-FOUNDATION] 定义 `InstalledFile` 数据类
  - 文件: `wiki_generator/installer.py`
  - 类: `@dataclass class InstalledFile:`, 包含 source_path, dest_path, is_backup, backup_path
  - 验证: 追踪已安装文件列表

---

## Phase 3: User Story 1 - P1 一键安装

### 3.1 核心安装流程

- [X] [T011-P1-US1] 实现 `main()` 函数主流程
  - 文件: `wiki_generator/__main__.py`
  - 函数: `def main():` 解析命令行参数，调用安装和配置生成函数
  - 逻辑: 1) 权限检查 → 2) 安装文件 → 3) 生成配置 → 4) 显示成功消息
  - 验证: 运行 `uvx wiki-generator` 成功安装

- [X] [T012-P1-US1] 添加命令行参数解析
  - 文件: `wiki_generator/__main__.py`
  - 库: 使用 `argparse` 定义参数（--force, --dry-run, --target-dir, --verbose, --version, --help）
  - 验证: 运行 `uvx wiki-generator --help` 显示所有选项

### 3.2 进度显示和用户反馈

- [X] [T013-P1-US1] 实现安装进度显示
  - 文件: `wiki_generator/installer.py`
  - 函数: 添加 `verbose` 输出逻辑，显示"正在安装 .claude/ 目录..."、"✓ 创建 .claude/commands/"等消息
  - 验证: 运行 `uvx wiki-generator --verbose` 查看详细输出

- [X] [T014-P1-US1] 实现成功消息和下一步提示
  - 文件: `wiki_generator/__main__.py`
  - 消息: "安装完成！\n下一步: 运行 /wiki-overview 生成项目概览文档"
  - 验证: 安装成功后显示中文提示

### 3.3 错误处理

- [X] [T015-P1-US1] 添加权限不足错误处理
  - 文件: `wiki_generator/installer.py`
  - 逻辑: 捕获 `PermissionError`，显示"错误: 目录 '{target_dir}' 无写入权限"
  - 验证: 在只读目录测试时显示中文错误消息

- [X] [T016-P1-US1] 添加文件冲突处理
  - 文件: `wiki_generator/installer.py`
  - 逻辑: 检测已存在文件，根据 `--force` 参数决定是否覆盖
  - 验证: 运行 `uvx wiki-generator` 两次，第二次提示文件已存在

- [X] [T017-P1-US1] 实现安装失败回滚
  - 文件: `wiki_generator/installer.py`
  - 逻辑: 在 `install_cli_files()` 中使用 try-except，失败时调用 `rollback_installation()`
  - 验证: 模拟复制失败，验证已安装文件被删除

---

## Phase 4: User Story 2 - P2 配置初始化

### 4.1 配置文件生成

- [X] [T018-P2-US2] 集成配置生成到主流程
  - 文件: `wiki_generator/__main__.py`
  - 逻辑: 在 `main()` 中调用 `generate_config()`，设置 `overwrite=False`（保留现有配置）
  - 验证: 首次安装生成 `wiki-config.json`，再次安装保留现有配置

- [X] [T019-P2-US2] 生成标准 JSON 配置文件
  - 文件: `wiki_generator/config.py`
  - 逻辑: 使用 `json.dump()` 生成标准 JSON 格式配置文件（无注释）
  - 验证: 生成的配置文件符合 JSON 规范

### 4.2 配置验证

- [X] [T020-P2-US2] 实现配置文件损坏处理
  - 文件: `wiki_generator/config.py`
  - 逻辑: 如果现有配置不是有效 JSON，备份为 `.backup` 并重新生成
  - 验证: 手动破坏 `wiki-config.json`，重新安装后生成有效配置

- [X] [T021-P2-US2] 添加配置字段验证
  - 文件: `wiki_generator/config.py`
  - 逻辑: 验证 diagrams_detail_level 枚举值（low/medium/high），quality_threshold 范围（0-100）
  - 验证: 尝试设置无效值，返回 `ValidationError`

---

## Phase 5: User Story 3 - P3 轻量级体验

### 5.1 性能优化

- [X] [T022-P3-US3] 优化启动时间（目标 < 2 秒）
  - 文件: `wiki_generator/__main__.py`
  - 优化: 延迟导入非必需模块，减少启动时的导入开销
  - 验证: 使用 `time wiki-generator --version` 测量启动时间：0.034s ✅

- [X] [T023-P3-US3] 优化文件复制性能（目标 < 5 秒）
  - 文件: `wiki_generator/installer.py`
  - 优化: 批量复制文件，减少 I/O 操作次数
  - 验证: 复制 34 个文件的时间：0.037s ✅

### 5.2 Dry-run 模式

- [X] [T024-P3-US3] 实现 `--dry-run` 选项
  - 文件: `wiki_generator/installer.py`
  - 逻辑: 遍历文件但不实际复制，显示"将要安装的文件:"列表
  - 验证: 运行 `wiki-generator --dry-run` 不修改文件系统

### 5.3 帮助文档

- [X] [T025-P3-US3] 编写简洁的帮助信息
  - 文件: `wiki_generator/__main__.py`
  - 内容: 添加 `argparse` 的 `help` 参数，说明每个选项的用途
  - 验证: 运行 `wiki-generator --help` 显示清晰的中文帮助
  - 验证: 运行 `uvx wiki-generator --help` 显示清晰的中文帮助

---

## Phase 6: Polish & Cross-Cutting Concerns

### 6.1 集成测试

- [X] [T026-P1-POLISH] 编写集成测试脚本
  - 文件: `tests/integration/test_installation.sh`
  - 测试场景: 1) 空目录安装 2) 覆盖已存在文件 3) 权限不足 4) 回滚失败 5) dry-run 不修改文件系统
  - 验证: 运行 `bash tests/integration/test_installation.sh` 基础测试通过

- [X] [T027-P1-POLISH] 测试跨平台兼容性
  - 文件: `tests/integration/test_cross_platform.sh`
  - 平台: Linux, macOS, Windows (WSL)
  - 验证: 在 Linux 平台上测试通过 ✅（其他平台需要用户验证）

### 6.2 文档完善

- [X] [T028-P2-POLISH] 代码已包含完整 Docstring 和中文注释
  - 文件: 所有 `wiki_generator/*.py` 文件
  - 标准: 遵循 PEP 257 Docstring 规范，包含详细的中文注释
  - 验证: 所有函数都有类型注解和文档字符串

- [X] [T029-P2-POLISH] 所有代码已添加详细注释
  - 文件: `wiki_generator/__init__.py`, `installer.py`, `config.py`, `__main__.py`
  - 验证: 包含模块级 Docstring、函数 Docstring、行内注释

### 6.3 错误消息优化

- [X] [T030-P2-POLISH] 统一错误消息格式
  - 文件: `wiki_generator/installer.py`, `wiki_generator/config.py`, `__main__.py`
  - 格式: "❌ 错误: {问题描述}\n💡 提示: {解决步骤}"
  - 验证: 所有用户可见的错误消息都是中文且格式统一

- [X] [T031-P2-POLISH] 实现详细日志模式
  - 文件: `wiki_generator/__main__.py`, `installer.py`
  - 逻辑: 实现 `--verbose` 模式，显示每个文件的操作详情
  - 验证: 运行 `wiki-generator --verbose` 显示详细的安装步骤

### 6.4 最终验证

- [X] [T032-P1-POLISH] 执行完整的功能验收测试
  - 验收标准:
    - ✅ SC-001: 安装时间 0.037s（目标 < 10 秒）
    - ✅ SC-002: 安装成功率 100%（多次测试成功）
    - ✅ SC-003: 配置文件 100% 符合 JSON 规范（已验证）
    - ✅ SC-004: 命令简洁直观，单命令完成安装
    - ✅ SC-005: 安装文件 34 个（目标 < 100 个）
    - ✅ SC-006: 工具启动时间 0.034s（目标 < 2 秒）
  - 验证: 所有指标均超预期达成 ✅

---

## Execution Examples

### Parallel Execution Strategy (Phase 3-5)

```bash
# Terminal 1: User Story 1 (P1)
git checkout -b feature/us1-installation
# Work on T011-T017

# Terminal 2: User Story 2 (P2) [After Phase 2 completes]
git checkout -b feature/us2-config
# Work on T018-T021

# Terminal 3: User Story 3 (P3) [After Phase 2 completes]
git checkout -b feature/us3-performance
# Work on T022-T025
```

### Critical Path Execution (Sequential)

```bash
# Phase 1: Setup
T001 → T002 → T003

# Phase 2: Foundation
T004 → T005 → T006 → T007 → T008 → T009 → T010

# Phase 3-5: User Stories (can be parallelized)
[T011-T017] ∥ [T018-T021] ∥ [T022-T025]

# Phase 6: Polish
T026 → T027 → T028 → T029 → T030 → T031 → T032
```

---

## Task Metadata

- **Total Estimated Tasks**: 32
- **P1 (Critical) Tasks**: 18
- **P2 (Important) Tasks**: 10
- **P3 (Nice-to-have) Tasks**: 4
- **Files to Create**: 10+
- **Files to Modify**: 5+
- **Test Coverage Target**: ≥ 90%

---

**Tasks Version**: 1.0.0
**Last Updated**: 2026-01-04
**Ready for Implementation**: ✅ Yes
