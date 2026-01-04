# Wiki Generator v2.0 测试指南

## 测试概述

本目录包含 Wiki Generator v2.0 的所有单元测试和集成测试。

## 测试结构

```
tests/test_v2/
├── __init__.py                      # 测试包初始化
├── test_config_validator.py         # 配置验证器测试
├── test_migrator.py                 # 配置迁移器测试
├── test_installer.py                # 文件安装器测试
├── test_template_manifest.py        # 模板清单测试
├── test_cli.py                      # CLI 命令测试
├── test_integration_init.py         # 完整初始化流程集成测试
├── test_integration_validate.py     # 配置验证流程集成测试
└── test_integration_migrate.py      # 迁移流程集成测试
```

## 运行测试

### 前置要求

安装测试依赖：

```bash
pip install pytest pytest-cov
```

### 运行所有测试

从项目根目录运行：

```bash
# 运行所有测试
pytest tests/test_v2/

# 运行测试并显示详细输出
pytest tests/test_v2/ -v

# 运行测试并生成覆盖率报告
pytest tests/test_v2/ --cov=wiki_generator --cov-report=html
```

### 运行单个测试文件

```bash
# 测试配置验证器
pytest tests/test_v2/test_config_validator.py -v

# 测试迁移工具
pytest tests/test_v2/test_migrator.py -v

# 测试文件安装器
pytest tests/test_v2/test_installer.py -v
```

### 运行特定测试类或方法

```bash
# 运行特定测试类
pytest tests/test_v2/test_config_validator.py::TestConfigValidator -v

# 运行特定测试方法
pytest tests/test_v2/test_config_validator.py::TestConfigValidator::test_validate_valid_minimal_config -v
```

### 运行集成测试

```bash
# 运行所有集成测试
pytest tests/test_v2/test_integration_*.py -v

# 运行特定集成测试
pytest tests/test_v2/test_integration_init.py -v
```

## 测试覆盖率目标

- **单元测试覆盖率**: ≥ 80%
- **关键模块覆盖率**: ≥ 90%
  - `config_validator.py`
  - `migrator.py`
  - `installer_v2.py`

## 测试编写规范

### 单元测试规范

1. **测试命名**: `test_<功能>_<场景>`
2. **测试类命名**: `Test<类名>`
3. **使用 fixture**: 优先使用 pytest fixture 进行设置
4. **独立性**: 每个测试应该独立运行，不依赖其他测试
5. **清理**: 使用 `tmp_path` fixture 自动清理临时文件

### 示例

```python
class TestConfigValidator:
    def test_validate_valid_config(self, validator, temp_config_file):
        """测试有效配置"""
        config_content = json.dumps({
            "output_dir": "docs",
            "language": "zh"
        })
        config_file = temp_config_file(config_content)

        result = validator.validate_config_file(config_file)

        assert result.is_valid
        assert len(result.errors) == 0
```

## 集成测试规范

1. **测试完整流程**: 从开始到结束测试真实场景
2. **使用真实文件**: 在临时目录中创建真实文件
3. **验证副作用**: 检查文件创建、修改等副作用
4. **清理资源**: 确保测试后清理所有创建的文件

## 当前测试状态

- [x] T066 配置验证测试
- [x] T067 迁移工具测试
- [x] T068 文件安装测试
- [ ] T069 模板清单测试
- [ ] T070 CLI 命令测试
- [ ] T071 完整初始化流程测试
- [ ] T072 配置验证流程测试
- [ ] T073 迁移流程测试

## 持续集成

测试应该在每次提交前运行：

```bash
# 运行测试并确保通过
pytest tests/test_v2/ -v --tb=short

# 检查测试覆盖率
pytest tests/test_v2/ --cov=wiki_generator --cov-report=term-missing
```

## 故障排除

### 常见问题

**问题**: 导入错误 `No module named 'wiki_generator'`

**解决方案**:
```bash
# 从项目根目录运行
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/test_v2/
```

**问题**: 测试失败 `FileNotFoundError`

**解决方案**: 确保从项目根目录运行测试

**问题**: 测试超时

**解决方案**: 增加超时时间
```bash
pytest tests/test_v2/ --timeout=300
```

## 贡献指南

添加新测试时：

1. 在对应的测试文件中添加测试方法
2. 确保测试命名清晰，描述测试场景
3. 使用适当的 fixture 和断言
4. 更新本文档的测试状态列表
5. 运行测试确保通过

---

**版本**: 2.0.0
**最后更新**: 2025-01-04
