# Wiki Generator 测试套件

本目录包含 Wiki Generator v3.1.0 增量更新功能的测试脚本。

## 快速开始

### 运行所有测试
```bash
# 在项目根目录执行
for test in tests/test_*.sh; do
    bash "$test"
done
```

### 运行单个测试文件
```bash
# 变更检测测试
bash tests/test_change_detection.sh

# 智能合并测试
bash tests/test_smart_merge.sh

# 集成测试
bash tests/test_incremental_updates.sh
```

## 测试文件

### test_helpers.sh
测试辅助函数库，提供：
- `setup_test_repo()` - 创建临时 Git 仓库
- `cleanup_test_repo()` - 清理测试仓库
- `create_test_file()` - 创建测试文件
- `assert_equals()` - 断言相等
- `assert_contains()` - 断言包含
- `assert_not_empty()` - 断言非空
- `assert_json_key()` - 断言 JSON 键值
- `run_test()` - 运行单个测试
- `print_test_summary()` - 打印测试摘要

### test_change_detection.sh
变更检测单元测试，包括：
- Git diff 分析测试
- 哈希计算测试（一致性、差异性）
- 排除模式过滤测试
- 空变更检测测试

### test_smart_merge.sh
智能合并单元测试，包括：
- 区域提取测试
- 手动编辑标记检测测试
- 多区域处理测试
- 相似度计算测试

### test_incremental_updates.sh
端到端集成测试，包括：
- 仓库管理测试
- 变更检测集成测试
- 文件哈希追踪测试
- 元数据路径计算测试
- 配置迁移测试
- 排除模式验证测试
- 区域标记验证测试

## 测试输出

### 成功示例
```
=========================================
变更检测单元测试
========================================

  Git diff 分析 ... ✓ PASS
  哈希计算一致性 ... ✓ PASS
  哈希计算差异性 ... ✓ PASS
  排除模式过滤 ... ✓ PASS
  空变更检测 ... ✓ PASS

=========================================
测试摘要
=========================================
总计:   5
通过:   5
失败:   0
=========================================
所有测试通过！
```

### 失败示例
```
=========================================
智能合并单元测试
========================================

  区域提取 ... ✓ PASS
  手动编辑检测 ... ✗ FAIL
  ❌Assertion failed: Should detect marker

=========================================
测试摘要
=========================================
总计:   2
通过:   1
失败:   1
=========================================
有测试失败
```

## 环境要求

### 必需
- Bash 4.0+
- Python 3.11+
- Git 2.0+

### 可选
- jq (JSON 处理工具，有 Python fallback)

## 故障排除

### 测试失败时
1. 查看详细错误消息
2. 检查环境是否符合要求
3. 尝试单独运行失败的测试
4. 查看 [CHANGE_DETECTION_TEST_PLAN.md](CHANGE_DETECTION_TEST_PLAN.md) 了解详情

### 权限错误
```bash
# 确保测试脚本可执行
chmod +x tests/test_*.sh
```

### Python 版本错误
```bash
# 检查 Python 版本
python3 --version

# 应该是 3.11 或更高
```

## 贡献指南

### 添加新测试
1. 在对应的测试文件中添加测试函数
2. 使用 `run_test` 在 `main()` 中注册
3. 更新测试计划文档

### 测试命名规范
- 测试函数: `test_<feature>_<scenario>()`
- 描述性名称: 清楚说明测试内容
- 一个测试一个关注点

### 断言使用
- 优先使用提供的断言函数
- 提供清晰的错误消息
- 清理测试资源（临时文件等）

## 相关文档

- [测试计划](CHANGE_DETECTION_TEST_PLAN.md) - 详细的测试策略和覆盖范围
- [架构设计](../docs/plans/004-wiki-generate.md) - 增量更新功能架构
- [配置 Schema](../plugins/schemas/wiki-config-schema-v3.json) - 配置验证

## 维护

- **维护者**: Claude Code
- **创建日期**: 2026-01-07
- **版本**: 3.1.0
