一个面向数据结构与算法学习场景的智能学习助手。  
项目结合 **RAG 问答**、**动态知识库构建**、**学习路径生成** 与 **层级化 topic tree**，支持从网络抓取算法资料、自动筛选与纳入知识库，并根据用户自然语言请求输出问答或学习路径。

---

## 1. 项目定位

学习数据结构与算法时，常见问题并不只是“这个概念是什么”，还包括：

- 这个知识点怎么学
- 先学什么后学什么
- 能举个例子吗
- 和其他算法有什么区别
- 有哪些细分主题值得继续深入

本项目的目标是构建一个 **面向算法学习场景的智能学习助手**，实现：

- 高质量资料检索与问答
- 动态知识库扩展
- 学习路径自动生成
- topic 层级组织与子主题推荐

---

## 2. 当前能力

### 2.1 问答模式
支持普通算法学习问答，例如：

- 动态规划定义
- 动态规划例子
- 动态规划与贪心有什么区别

系统流程：

```text
用户问题
→ embedding + FAISS 召回
→ 语义去重
→ rerank 精排
→ 大模型生成答案
→ 输出参考来源
2.2 学习路径模式

支持自然语言形式的学习路径请求，例如：

我想系统学习动态规划
给我一个动态规划学习路线
完全背包问题怎么学
记忆化搜索怎么学

系统会输出：

知识点
父主题
前置知识
学习步骤
推荐资料
子主题
2.3 动态知识库更新

支持从网络获取资料并自动纳入知识库：

输入文章 URL
→ 网页正文抓取
→ AI 质量筛选与分类
→ 相似度检测
→ AI 冲突仲裁
→ 保存到 data/
→ 自动重建索引
→ 自动更新 learning path
2.4 Topic Tree（知识点层级结构）

系统中的 topic 不再是平铺列表，而是带有父子关系，例如：

动态规划
动态规划与背包问题
动态规划-完全背包问题
动态规划-记忆化搜索
动态规划-双串线性DP

这使系统能够从“资料检索”进一步升级为“结构化学习辅助”。

3. 主要技术设计
3.1 检索增强问答
使用 Sentence-Transformers 生成文本 embedding
使用 FAISS 建立向量索引
使用规则化 rerank 区分学习意图（定义 / 例子 / 区别 / 题解等）
使用 OpenAI 模型基于上下文生成最终回答
3.2 动态资料纳入
fetch.py：网页抓取与正文抽取
filter.py：AI 判断资料是否适合纳入知识库
dedup.py：与现有知识库做语义重复检测
resolve_conflict.py：若资料高度重复，则让 AI 在新旧资料中选择质量更高的一份
ingest.py：写入 data/ 并自动重建索引
3.3 学习路径生成
generate_path.py：根据 topic 和资料内容自动生成
前置知识
学习步骤
knowledge_map.json：保存 topic 的结构化学习信息
pathway.py：读取学习路径，并支持父主题 / 子主题查询
3.4 自然语言意图识别与 topic 对齐
classifier.py：判断用户输入属于
qa（普通问答）
path（学习路径）
topic_matcher.py：
规则优先
embedding 粗筛
API 兜底
将用户口语表达对齐到系统内部标准 topic

例如：

完全背包问题 → 动态规划-完全背包问题
记忆化搜索 → 动态规划-记忆化搜索
双串dp → 动态规划-双串线性DP
4. 项目结构
algo_tutor_agent/
│
├── data/                         # 知识库 Markdown 文档
├── vector_store/                 # FAISS 索引与 chunk 元数据
├── collector/                    # 动态资料采集与知识库更新模块
│   ├── __init__.py
│   ├── fetch.py
│   ├── filter.py
│   ├── dedup.py
│   ├── resolve_conflict.py
│   ├── generate_path.py
│   ├── generate_parent.py
│   └── ingest.py
│
├── rag/                          # 检索、路径、分类与 topic 对齐模块
│   ├── __init__.py
│   ├── embed.py
│   ├── index.py
│   ├── retrieve.py
│   ├── rerank.py
│   ├── qa.py
│   ├── pathway.py
│   ├── classifier.py
│   └── topic_matcher.py
│
├── scripts/
│   └── fill_missing_paths.py     # 批量补全空壳 topic 的学习路径
│
├── knowledge_map.json            # topic tree + 学习路径结构数据
├── config.py
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
5. 环境准备

建议使用 Python 3.10。

5.1 创建环境
conda create -n rag python=3.10 -y
conda activate rag
5.2 安装依赖
pip install -r requirements.txt
6. 配置 API Key

在环境变量中设置：

PowerShell
$env:OPENAI_API_KEY="your_api_key"
7. 构建知识库索引

首次运行或更新 data/ 后，执行：

python -m rag.index
8. 启动项目
python main.py
9. 使用示例
9.1 学习路径类请求
我想系统学习动态规划
给我一个动态规划学习路线
完全背包问题怎么学
记忆化搜索怎么学
9.2 普通问答类请求
动态规划与贪心有什么区别
动态规划例子
动态规划定义

根据当前测试结果，这些自然语言请求已经可以正确区分为学习路径或问答模式，并返回相应内容。

10. 动态纳入新资料

执行：

python -m collector.ingest

然后输入文章 URL，例如算法教程文章链接。

系统会自动完成：

网页抓取
AI 质量筛选
topic 分类
相似度检测
冲突仲裁
知识库写入
learning path 更新
索引重建
11. 补全历史空壳 topic

如果某些旧 topic 只有资源，没有前置知识和学习步骤，可以执行：

python scripts/fill_missing_paths.py

系统会自动读取资源文件并补全其学习路径。

12. 当前亮点
12.1 不只是普通 RAG

本项目不只是“检索 + 回答”，而是进一步面向算法学习场景引入：

学习路径
细粒度 topic
topic tree
动态知识库更新
12.2 动态知识库治理

对于新资料，系统不仅会纳入知识库，还会进行：

AI 初筛
相似度检测
AI 冲突仲裁
自动替换更优资料
12.3 自然语言学习路径请求

用户不需要记忆固定命令，例如无需强制输入“学习路径 动态规划”，也可以直接说：

我想系统学习动态规划
完全背包问题怎么学
12.4 Topic 对齐

系统能够把用户自然表达自动映射为标准知识点名称，从而提升学习路径匹配成功率。