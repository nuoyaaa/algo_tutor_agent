# Algo Tutor Agent

一个面向数据结构与算法学习场景的智能学习助手。项目结合了检索增强问答（RAG）、学习路径推荐、下一知识点推荐，以及知识库增量更新能力，目标不是只回答“这是什么”，而是帮助用户持续学习“下一步该学什么”。

## 项目概览

这个项目围绕算法学习做了三件事：

1. 回答问题  
   基于本地知识库检索相关资料，并用大模型生成简洁回答，同时附上参考来源。

2. 规划学习路径  
   针对某个知识点返回前置知识、学习步骤、推荐资料和子主题，适合系统化学习。

3. 持续扩充知识库  
   支持输入文章 URL，自动抓取正文、筛选质量、去重、冲突决策、写入 `data/`，并重建向量索引与学习路径。

## 当前能力

### 1. 普通问答

适合这类输入：

- `动态规划定义`
- `动态规划例子`
- `动态规划和贪心有什么区别`

处理流程：

```text
用户问题
-> embedding 检索
-> 语义去重
-> rerank 精排
-> 基于上下文生成答案
-> 返回参考来源
```

### 2. 学习路径推荐

适合这类输入：

- `我想系统学习动态规划`
- `完全背包问题怎么学`
- `给我一个动态规划学习路线`

系统会返回：

- 知识点名称
- 父主题
- 前置知识
- 学习步骤
- 推荐资料
- 子主题

### 3. 下一知识点推荐

适合这类输入：

- `动态规划学完以后学什么`
- `推荐下一个知识点 动态规划`
- `学习完完全背包后下一步学什么`

系统会优先从当前主题的子主题中推荐候选项，并生成简短推荐理由。

### 4. 知识库增量更新

执行 `collector.ingest` 后，系统支持：

- 抓取网页正文
- 判断内容是否值得纳入知识库
- 与现有资料做语义去重
- 在相似资料之间做保留/替换决策
- 自动写入 `data/`
- 更新 `knowledge_map.json`
- 重建 FAISS 索引

## 技术设计

### 检索与问答

- `sentence-transformers/all-MiniLM-L6-v2` 负责文本向量化
- `FAISS` 负责向量检索
- `rag/rerank.py` 负责检索结果精排
- OpenAI 模型负责意图分类、答案生成和推荐理由生成

### 学习路径与知识结构

- `knowledge_map.json` 保存 topic 的结构化学习信息
- `rag/pathway.py` 读取学习路径与父子主题关系
- `rag/topic_matcher.py` 将用户口语表达映射到标准 topic
- `rag/next_topic.py` 基于 topic tree 推荐下一知识点

### 知识采集

- `collector/fetch.py` 抓取网页正文
- `collector/filter.py` 评估资料质量与主题分类
- `collector/dedup.py` 检查语义重复
- `collector/resolve_conflict.py` 决定保留新资料还是旧资料
- `collector/generate_path.py` 自动生成学习路径
- `collector/generate_parent.py` 自动推断父主题

## 项目结构

```text
algo_tutor_agent/
├─ collector/              # 资料抓取、筛选、去重、纳入知识库
├─ data/                   # 本地 Markdown 知识库
├─ rag/                    # 检索、问答、路径推荐、topic 匹配
├─ scripts/                # 数据维护脚本
├─ vector_store/           # FAISS 索引与检索元数据
├─ knowledge_map.json      # topic tree 与学习路径数据
├─ config.py               # 模型与路径配置
├─ main.py                 # CLI 入口
├─ requirements.txt
└─ README.md
```

## 环境准备

推荐 Python 3.10。

### 1. 创建虚拟环境

```powershell
conda create -n algo-tutor python=3.10 -y
conda activate algo-tutor
```

### 2. 安装依赖

```powershell
pip install -r requirements.txt
```

### 3. 配置 API Key

复制 `.env.example` 或直接设置环境变量：

```powershell
$env:OPENAI_API_KEY="your_openai_api_key"
```

## 快速开始

### 1. 构建向量索引

首次运行，或更新了 `data/` 中的知识库内容后，先执行：

```powershell
python -m rag.index
```

### 2. 启动命令行助手

```powershell
python main.py
```

输入 `exit`、`quit` 或 `q` 可以退出。

## 使用示例

### 普通问答

```text
动态规划和贪心有什么区别
动态规划例子
动态规划定义
```

### 学习路径

```text
我想系统学习动态规划
给我一个动态规划学习路线
记忆化搜索怎么学
```

### 下一知识点推荐

```text
动态规划学完以后学什么
推荐下一个知识点 动态规划
完全背包学完后下一步学什么
```

## 知识库维护

### 纳入新资料

```powershell
python -m collector.ingest
```

然后输入文章 URL。系统会自动完成抓取、筛选、去重、写入和索引更新。

### 补全历史 topic 的学习路径

如果某些 topic 已有资源，但 `prerequisites` 或 `steps` 仍为空，可以执行：

```powershell
python scripts/fill_missing_paths.py
```

## 核心文件说明

- `main.py`：程序入口，负责接收输入并分发到问答、学习路径或下一主题推荐流程
- `rag/classifier.py`：识别用户意图，区分 `qa`、`path`、`next_topic`
- `rag/qa.py`：执行检索并生成回答
- `rag/pathway.py`：读取知识路径与子主题
- `rag/next_topic.py`：推荐下一个可继续学习的主题
- `collector/ingest.py`：资料入库主流程
- `knowledge_map.json`：项目最关键的结构化知识地图

## 适合继续改进的方向

- 增加 Web 界面或 API 服务层
- 为 `knowledge_map.json` 提供可视化展示
- 增加测试用例与评估脚本
- 支持更多算法主题与更细的 topic tree
- 把知识采集流程改造成批量任务
