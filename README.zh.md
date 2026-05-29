# autoplot-uav-cli

大疆无人机 KML 航线规划工具，根据地块边界和作业配置生成 KMZ 航点任务文件。

## 安装

### 前置要求

安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 获取代码并安装依赖

```bash
git clone https://github.com/zhzyx/autoplot-uav-cli.git
cd autoplot-uav-cli
uv sync
```

开发环境（含 Jupyter 和 pytest）：

```bash
uv sync --extra dev
```

## 使用

```bash
uv run survey --config mission_cfg/your_config.yaml
```

或激活虚拟环境后直接运行：

```bash
source .venv/bin/activate
python survey_gen.py --config mission_cfg/your_config.yaml
```

## 测试

```bash
uv run pytest
```

## 任务配置

任务 YAML 文件放在 `mission_cfg/` 目录下，可参考已有配置文件。

## 项目结构

```
src/
  kml/            # KMZ/KML 文件生成
  task_planner/   # 网格规划与地块作业
  cmd_tools/      # 坐标转换工具
tests/
mission_cfg/      # 任务配置 YAML
```
