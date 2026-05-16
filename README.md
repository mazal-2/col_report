# Report Writer

数据分析与报告生成工具

## 项目结构

```
report_writer/
├── main.py                    # 入口文件
├── pyproject.toml             # 项目配置
│
├── src/                       # 源代码
│   ├── report/                # 报告生成模块
│   │   ├── build_combined_report.py      # 综合运营分析报告
│   │   ├── build_content_docx.py         # 内容趋势分析报告
│   │   ├── build_publish_erchuang_docx.py # 上架趋势与二创对比报告
│   │   ├── generate_report.py            # 运营分析报告
│   │   └── generate_drama_doc.py         # 剧目标签文档
│   │
│   ├── analysis/              # 数据分析模块
│   │   ├── generate_content_trend.py     # 内容趋势图表生成
│   │   ├── build_publish_erchuang.py     # 上架趋势与二创数据处理
│   │   ├── calc_erchuang.py              # 二创数据计算
│   │   └── stats.py                      # 统计数据
│   │
│   ├── data/                  # 数据处理模块
│   │   ├── complete_tags.py              # 完善剧目标签
│   │   ├── extract_drama.py              # 提取剧目描述
│   │   └── output_drama_csv.py           # 输出剧目标签CSV
│   │
│   └── fetch/                 # 数据获取模块
│       ├── fetch_wechat_video.py         # 获取微信视频数据
│       ├── fetch_works_list.py           # 获取剧目列表
│       ├── check_iaa.py                  # 检查IAA数据
│       ├── check_works.py                # 检查剧目数据
│       ├── debug_works.py                # 调试剧目数据
│       ├── export_works_csv.py           # 导出剧目CSV
│       ├── json_to_excel.py              # JSON转Excel
│       └── verify_iaa.py                 # 验证IAA数据
│
├── scripts/                   # 临时脚本与数据文件
│   ├── fetched_data.json     # 获取的原始数据
│   ├── works_list.json       # 剧目列表
│   └── temp_file/            # 临时文件
│
├── prompts/                   # 报告模板
│   ├── content_trend.md      # 内容趋势模板
│   ├── format.md             # 格式模板
│   └── publish_trend_erchaung.md # 二创对比模板
│
├── data/                      # 输入数据文件
├── charts/                    # 生成的图表
├── docs/                      # 输出文档
└── output/                    # 报告输出目录
```

## 使用方法

```bash
# 安装依赖
pip install -e .

# 运行报告生成
python src/report/build_combined_report.py
```

## 功能说明

### 报告生成模块 (src/report/)
- 生成各类运营分析报告（Word格式）
- 支持图表嵌入、表格生成

### 数据分析模块 (src/analysis/)
- 日频/周频/月频数据分析
- 男女频、题材维度对比
- 二创账号对比分析

### 数据处理模块 (src/data/)
- 剧目标签管理
- 数据格式转换

### 数据获取模块 (src/fetch/)
- 微信视频号数据获取
- 数据验证与导出
