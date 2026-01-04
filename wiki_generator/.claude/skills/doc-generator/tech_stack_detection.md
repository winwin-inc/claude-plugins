# 技术栈检测 Skill

**功能**: 自动检测项目使用的 20+ 技术栈和框架

**检测方法**: 使用 `grep`、`find` 等工具扫描项目文件，识别导入语句、配置文件、依赖声明

**性能目标**: 检测时间 < 5 秒（中型项目）

---

## 核心检测函数

### detect_tech_stack()

```bash
#!/usr/bin/env bash
# 技术栈检测主函数
# 用法: detect_tech_stack <project_dir>

detect_tech_stack() {
    local project_dir=$1
    local tech_stack=()
    local src_dir="$project_dir/src"

    # 如果 src/ 不存在，尝试其他常见目录
    if [ ! -d "$src_dir" ]; then
        if [ -d "$project_dir/app" ]; then
            src_dir="$project_dir/app"
        else
            src_dir="$project_dir"
        fi
    fi

    # 排除测试目录和缓存目录
    local exclude_dirs="--exclude-dir=tests --exclude-dir=test --exclude-dir=__pycache__ --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build"

    # 1. 后端框架检测（4 种）
    tech_stack+=($(detect_backend_frameworks "$src_dir" "$exclude_dirs"))

    # 2. ORM 检测（3 种）
    tech_stack+=($(detect_orms "$src_dir" "$exclude_dirs"))

    # 3. CLI 框架检测（3 种）
    tech_stack+=($(detect_cli_frameworks "$src_dir" "$exclude_dirs"))

    # 4. 前端框架检测（3 种）
    tech_stack+=($(detect_frontend_frameworks "$project_dir" "$src_dir" "$exclude_dirs"))

    # 5. 任务队列检测（2 种）
    tech_stack+=($(detect_task_queues "$src_dir" "$exclude_dirs"))

    # 6. 消息队列检测（2 种）
    tech_stack+=($(detect_message_queues "$src_dir" "$exclude_dirs"))

    # 7. 数据库检测（3 种）
    tech_stack+=($(detect_databases "$project_dir" "$src_dir" "$exclude_dirs"))

    # 8. 缓存检测（2 种）
    tech_stack+=($(detect_caches "$src_dir" "$exclude_dirs"))

    # 9. 容器化检测（3 种）
    tech_stack+=($(detect_containerization "$project_dir"))

    # 10. API 规范检测（3 种）
    tech_stack+=($(detect_api_specs "$src_dir" "$exclude_dirs"))

    # 去重（同一类别只保留最高优先级）
    tech_stack=($(deduplicate_tech_stack "${tech_stack[@]}"))

    echo "${tech_stack[@]}"
}
```

---

## 1. 后端框架检测

```bash
detect_backend_frameworks() {
    local src_dir=$1
    local exclude_dirs=$2
    local frameworks=()

    # FastAPI
    if grep -rq "from fastapi" "$src_dir" $exclude_dirs 2>/dev/null || \
       grep -rq "import fastapi" "$src_dir" $exclude_dirs 2>/dev/null; then
        frameworks+=("fastapi")
    fi

    # Flask
    if grep -rq "from flask" "$src_dir" $exclude_dirs 2>/dev/null; then
        frameworks+=("flask")
    fi

    # Django
    if grep -rq "from django" "$src_dir" $exclude_dirs 2>/dev/null || \
       grep -rq "import django" "$src_dir" $exclude_dirs 2>/dev/null || \
       [ -f "$(dirname "$src_dir")/manage.py" ]; then
        frameworks+=("django")
    fi

    # Tornado
    if grep -rq "import tornado" "$src_dir" $exclude_dirs 2>/dev/null || \
       grep -rq "from tornado" "$src_dir" $exclude_dirs 2>/dev/null; then
        frameworks+=("tornado")
    fi

    echo "${frameworks[@]}"
}
```

---

## 2. ORM 检测

```bash
detect_orms() {
    local src_dir=$1
    local exclude_dirs=$2
    local orms=()

    # SQLAlchemy
    if grep -rq "from sqlalchemy" "$src_dir" $exclude_dirs 2>/dev/null || \
       grep -rq "import sqlalchemy" "$src_dir" $exclude_dirs 2>/dev/null; then
        orms+=("sqlalchemy")
    fi

    # Django ORM
    if grep -rq "from django.db" "$src_dir" $exclude_dirs 2>/dev/null; then
        orms+=("django-orm")
    fi

    # Tortoise ORM
    if grep -rq "from tortoise" "$src_dir" $exclude_dirs 2>/dev/null || \
       grep -rq "import tortoise" "$src_dir" $exclude_dirs 2>/dev/null; then
        orms+=("tortoise-orm")
    fi

    echo "${orms[@]}"
}
```

---

## 3. CLI 框架检测

```bash
detect_cli_frameworks() {
    local src_dir=$1
    local exclude_dirs=$2
    local frameworks=()

    # Click
    if grep -rq "import click" "$src_dir" $exclude_dirs 2>/dev/null || \
       grep -rq "from click" "$src_dir" $exclude_dirs 2>/dev/null; then
        frameworks+=("click")
    fi

    # Typer
    if grep -rq "import typer" "$src_dir" $exclude_dirs 2>/dev/null || \
       grep -rq "from typer" "$src_dir" $exclude_dirs 2>/dev/null; then
        frameworks+=("typer")
    fi

    # argparse (标准库)
    if grep -rq "import argparse" "$src_dir" $exclude_dirs 2>/dev/null; then
        frameworks+=("argparse")
    fi

    echo "${frameworks[@]}"
}
```

---

## 4. 前端框架检测

```bash
detect_frontend_frameworks() {
    local project_dir=$1
    local src_dir=$2
    local exclude_dirs=$3
    local frameworks=()

    # React（检查 package.json）
    if [ -f "$project_dir/package.json" ]; then
        if grep -q '"react"' "$project_dir/package.json" 2>/dev/null || \
           grep -q '"@types/react"' "$project_dir/package.json" 2>/dev/null; then
            frameworks+=("react")
        fi
    fi

    # Vue（检查 package.json）
    if [ -f "$project_dir/package.json" ]; then
        if grep -q '"vue"' "$project_dir/package.json" 2>/dev/null || \
           grep -q '"@vitejs/plugin-vue"' "$project_dir/package.json" 2>/dev/null; then
            frameworks+=("vue")
        fi
    fi

    # Streamlit（检查导入）
    if grep -rq "import streamlit" "$src_dir" $exclude_dirs 2>/dev/null || \
       grep -rq "import streamlit" "$src_dir" $exclude_dirs 2>/dev/null; then
        frameworks+=("streamlit")
    fi

    echo "${frameworks[@]}"
}
```

---

## 5. 任务队列检测

```bash
detect_task_queues() {
    local src_dir=$1
    local exclude_dirs=$2
    local queues=()

    # Celery
    if grep -rq "from celery" "$src_dir" $exclude_dirs 2>/dev/null || \
       grep -rq "import celery" "$src_dir" $exclude_dirs 2>/dev/null; then
        queues+=("celery")
    fi

    # RQ (Redis Queue)
    if grep -rq "from rq" "$src_dir" $exclude_dirs 2>/dev/null || \
       grep -rq "import rq" "$src_dir" $exclude_dirs 2>/dev/null; then
        queues+=("rq")
    fi

    echo "${queues[@]}"
}
```

---

## 6. 消息队列检测

```bash
detect_message_queues() {
    local src_dir=$1
    local exclude_dirs=$2
    local queues=()

    # Kafka
    if grep -rq "from kafka" "$src_dir" $exclude_dirs 2>/dev/null || \
       grep -rq "import kafka" "$src_dir" $exclude_dirs 2>/dev/null || \
       grep -rq "aiokafka" "$src_dir" $exclude_dirs 2>/dev/null; then
        queues+=("kafka")
    fi

    # RabbitMQ
    if grep -rq "from pika" "$src_dir" $exclude_dirs 2>/dev/null || \
       grep -rq "import pika" "$src_dir" $exclude_dirs 2>/dev/null; then
        queues+=("rabbitmq")
    fi

    echo "${queues[@]}"
}
```

---

## 7. 数据库检测

```bash
detect_databases() {
    local project_dir=$1
    local src_dir=$2
    local exclude_dirs=$3
    local databases=()

    # 检查依赖文件（requirements.txt、pyproject.toml、setup.py）
    local dep_files=(
        "$project_dir/requirements.txt"
        "$project_dir/pyproject.toml"
        "$project_dir/setup.py"
    )

    # PostgreSQL
    for dep_file in "${dep_files[@]}"; do
        if [ -f "$dep_file" ]; then
            if grep -qi "psycopg" "$dep_file" 2>/dev/null || \
               grep -qi "postgresql" "$dep_file" 2>/dev/null; then
                databases+=("postgresql")
                break
            fi
        fi
    done

    # MySQL
    for dep_file in "${dep_files[@]}"; do
        if [ -f "$dep_file" ]; then
            if grep -qi "pymysql" "$dep_file" 2>/dev/null || \
               grep -qi "mysqlclient" "$dep_file" 2>/dev/null || \
               grep -qi "mysql" "$dep_file" 2>/dev/null; then
                databases+=("mysql")
                break
            fi
        fi
    done

    # MongoDB
    for dep_file in "${dep_files[@]}"; do
        if [ -f "$dep_file" ]; then
            if grep -qi "pymongo" "$dep_file" 2>/dev/null || \
               grep -qi "mongodb" "$dep_file" 2>/dev/null; then
                databases+=("mongodb")
                break
            fi
        fi
    done

    echo "${databases[@]}"
}
```

---

## 8. 缓存检测

```bash
detect_caches() {
    local src_dir=$1
    local exclude_dirs=$2
    local caches=()

    # Redis
    if grep -rq "import redis" "$src_dir" $exclude_dirs 2>/dev/null || \
       grep -rq "from redis" "$src_dir" $exclude_dirs 2>/dev/null; then
        caches+=("redis")
    fi

    # Memcached
    if grep -rq "import memcache" "$src_dir" $exclude_dirs 2>/dev/null || \
       grep -rq "from memcache" "$src_dir" $exclude_dirs 2>/dev/null; then
        caches+=("memcached")
    fi

    echo "${caches[@]}"
}
```

---

## 9. 容器化检测

```bash
detect_containerization() {
    local project_dir=$1
    local containers=()

    # Dockerfile
    if [ -f "$project_dir/Dockerfile" ]; then
        containers+=("dockerfile")
    fi

    # docker-compose
    if [ -f "$project_dir/docker-compose.yml" ] || \
       [ -f "$project_dir/docker-compose.yaml" ]; then
        containers+=("docker-compose")
    fi

    # Kubernetes
    if [ -d "$project_dir/k8s" ] || \
       [ -d "$project_dir/kubernetes" ] || \
       [ -f "$project_dir/deployment.yaml" ] || \
       [ -f "$project_dir/deployment.yml" ]; then
        containers+=("kubernetes")
    fi

    echo "${containers[@]}"
}
```

---

## 10. API 规范检测

```bash
detect_api_specs() {
    local src_dir=$1
    local exclude_dirs=$2
    local specs=()

    # OpenAPI/Swagger
    if grep -rq "from fastapi.openapi" "$src_dir" $exclude_dirs 2>/dev/null || \
       grep -rq "swagger" "$src_dir" $exclude_dirs 2>/dev/null; then
        specs+=("openapi")
    fi

    # GraphQL
    if grep -rq "import graphql" "$src_dir" $exclude_dirs 2>/dev/null || \
       grep -rq "from graphql" "$src_dir" $exclude_dirs 2>/dev/null || \
       grep -rq "strawberry" "$src_dir" $exclude_dirs 2>/dev/null; then
        specs+=("graphql")
    fi

    # gRPC
    if grep -rq "import grpc" "$src_dir" $exclude_dirs 2>/dev/null || \
       grep -rq "from grpc" "$src_dir" $exclude_dirs 2>/dev/null || \
       [ -f "$(dirname "$src_dir")/*.proto" ]; then
        specs+=("grpc")
    fi

    echo "${specs[@]}"
}
```

---

## 技术栈去重逻辑

**优先级规则**（保留最高优先级）：

| 类别 | 优先级（高→低） |
|------|----------------|
| 后端框架 | FastAPI > Flask > Django > Tornado |
| ORM | SQLAlchemy > Django ORM > Tortoise ORM |
| 前端框架 | React > Vue > Streamlit |
| 消息队列 | Kafka > RabbitMQ |

```bash
deduplicate_tech_stack() {
    local tech_stack=("$@")
    local unique_stack=()
    local seen_backend=""
    local seen_orm=""
    local seen_frontend=""
    local seen_mq=""

    for tech in "${tech_stack[@]}"; do
        case "$tech" in
            fastapi|flask|django|tornado)
                if [ -z "$seen_backend" ]; then
                    unique_stack+=("$tech")
                    seen_backend="$tech"
                fi
                ;;
            sqlalchemy|django-orm|tortoise-orm)
                if [ -z "$seen_orm" ]; then
                    unique_stack+=("$tech")
                    seen_orm="$tech"
                fi
                ;;
            react|vue|streamlit)
                if [ -z "$seen_frontend" ]; then
                    unique_stack+=("$tech")
                    seen_frontend="$tech"
                fi
                ;;
            kafka|rabbitmq)
                if [ -z "$seen_mq" ]; then
                    unique_stack+=("$tech")
                    seen_mq="$tech"
                fi
                ;;
            *)
                # 其他类别直接添加
                unique_stack+=("$tech")
                ;;
        esac
    done

    echo "${unique_stack[@]}"
}
```

---

## 检测失败处理

**降级策略**：

1. 如果没有任何技术栈被检测到：
   - 生成警告："⚠️ 未检测到任何已知技术栈"
   - 生成基础文档（快速开始、项目概述）
   - 提供手动配置指南（在 `wiki-config.json` 中指定技术栈）

2. 如果检测不完整（部分技术栈）：
   - 使用检测到的技术栈生成对应文档
   - 对未检测到的部分，生成通用文档

```bash
# 检测失败处理示例
tech_stack=($(detect_tech_stack "$project_dir"))

if [ ${#tech_stack[@]} -eq 0 ]; then
    echo "⚠️ 警告: 未检测到任何已知技术栈" >&2
    echo "💡 提示: 可以在 wiki-config.json 中手动指定技术栈" >&2
    echo "" >&2
    echo "{" >&2
    echo "  \"tech_stack\": [\"fastapi\", \"sqlalchemy\", \"redis\"]" >&2
    echo "}" >&2
    # 生成基础文档
    generate_base_docs_only "$project_dir"
    exit 1
fi
```

---

## 使用示例

```bash
# 检测当前项目的技术栈
project_dir="/path/to/project"
tech_stack=($(detect_tech_stack "$project_dir"))

echo "检测到的技术栈:"
for tech in "${tech_stack[@]}"; do
    echo "  - $tech"
done
```

**输出示例**：

```
检测到的技术栈:
  - fastapi
  - sqlalchemy
  - redis
  - dockerfile
  - openapi
```

---

**版本**: 1.0.0
**最后更新**: 2026-01-04
