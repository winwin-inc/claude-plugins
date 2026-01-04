"""配置验证器。

此模块负责验证 Wiki 配置文件是否符合 JSON Schema。
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from jsonschema import validate, ValidationError
except ImportError:
    # 如果 jsonschema 未安装，提供占位符
    def validate(instance, schema):
        raise ImportError("需要安装 jsonschema: pip install jsonschema")

    class ValidationError(Exception):
        pass

from wiki_generator.models.config_models import ValidationResult
from wiki_generator.core.schema_loader import SchemaLoader, get_default_loader
from wiki_generator.utils.file_utils import read_file_content


class ConfigValidator:
    """配置验证器。

    使用 JSON Schema 验证 Wiki 配置文件。
    """

    def __init__(self, schema_loader: Optional[SchemaLoader] = None):
        """初始化配置验证器。

        Args:
            schema_loader: Schema 加载器。如果为 None，使用默认加载器。
        """
        self.schema_loader = schema_loader or get_default_loader()

    def validate_config_file(
        self,
        config_path: Path,
        schema_name: str = "wiki-config-schema-v2.json"
    ) -> ValidationResult:
        """验证配置文件。

        Args:
            config_path: 配置文件路径
            schema_name: Schema 文件名

        Returns:
            验证结果
        """
        # 读取配置文件
        content = read_file_content(config_path)
        if content is None:
            return ValidationResult(
                is_valid=False,
                errors=[f"无法读取配置文件: {config_path}"],
                config_path=str(config_path)
            )

        # 解析 JSON
        try:
            config_data = json.loads(content)
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"JSON 解析失败: {str(e)}"],
                config_path=str(config_path)
            )

        # 加载 Schema
        schema = self.schema_loader.load_schema(schema_name)
        if schema is None:
            return ValidationResult(
                is_valid=False,
                errors=[f"无法加载 Schema: {schema_name}"],
                config_path=str(config_path)
            )

        # 验证
        return self._validate_with_schema(config_data, schema, str(config_path))

    def validate_config_data(
        self,
        config_data: Dict[str, Any],
        schema_name: str = "wiki-config-schema-v2.json"
    ) -> ValidationResult:
        """验证配置数据。

        Args:
            config_data: 配置数据字典
            schema_name: Schema 文件名

        Returns:
            验证结果
        """
        # 加载 Schema
        schema = self.schema_loader.load_schema(schema_name)
        if schema is None:
            return ValidationResult(
                is_valid=False,
                errors=[f"无法加载 Schema: {schema_name}"]
            )

        return self._validate_with_schema(config_data, schema)

    def _validate_with_schema(
        self,
        config_data: Dict[str, Any],
        schema: Dict[str, Any],
        config_path: Optional[str] = None
    ) -> ValidationResult:
        """使用 Schema 验证配置数据。

        Args:
            config_data: 配置数据
            schema: JSON Schema
            config_path: 配置文件路径（可选）

        Returns:
            验证结果
        """
        errors = []
        warnings = []

        try:
            validate(instance=config_data, schema=schema)
        except ValidationError as e:
            # 格式化错误消息
            errors.append(self._format_validation_error(e))

        # 检查警告条件
        warnings.extend(self._check_warnings(config_data))

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            config_path=config_path
        )

    def _format_validation_error(self, error: ValidationError) -> str:
        """格式化验证错误消息。

        Args:
            error: jsonschema.ValidationError

        Returns:
            格式化的错误消息
        """
        path = " -> ".join(str(p) for p in error.path) if error.path else "根"
        message = error.message

        # 翻译常见的英文错误消息为中文
        message = self._translate_error_message(message)

        return f"字段 '{path}': {message}"

    def _translate_error_message(self, message: str) -> str:
        """翻译英文错误消息为中文。

        Args:
            message: 英文错误消息

        Returns:
            中文错误消息
        """
        translations = {
            "is a required property": "是必需字段",
            "must be one of": "必须是以下值之一",
            "does not match": "不匹配",
            "is not valid under any of the given schemas": "不符合任何给定的 schema",
            "is not of type": "类型错误",
            "should be non-empty": "不能为空",
        }

        for eng, chi in translations.items():
            if eng in message:
                message = message.replace(eng, chi)

        return message

    def _check_warnings(self, config_data: Dict[str, Any]) -> list[str]:
        """检查配置警告。

        Args:
            config_data: 配置数据

        Returns:
            警告列表
        """
        warnings = []

        # 检查 output_dir 是否为常见目录
        output_dir = config_data.get("output_dir", "docs")
        if output_dir in ["src", "lib", "bin", "etc"]:
            warnings.append(f"output_dir '{output_dir}' 可能与系统目录冲突")

        # 检查是否使用 custom 模式但没有定义 sections
        if config_data.get("structure_template") == "custom":
            if "sections" not in config_data or not config_data["sections"]:
                warnings.append("使用 'custom' 模式但未定义 sections")

        return warnings
