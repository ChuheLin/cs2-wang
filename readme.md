# CS2.wang - CS2 饰品价值投资分析平台

> 专注饰品价值投资组合，CS 饰品价值投资教父

[![Website](https://img.shields.io/badge/Website-cs2.wang-blue)](https://cs2.wang)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📖 项目简介

CS2.wang 是一个专注于 Counter-Strike 2（CS2）饰品市场价值投资分析的平台。本项目通过量化分析、市场研报和每日战报，为 CS2 饰品投资者提供专业的投资参考和市场洞察。

**特别说明**：本项目完完全全由 Gemini 创建，DeepSeek 运营。

## ✨ 主要功能

- 📊 **全市场量化扫描**：通过量化模型寻找被错杀的黄金资产
- 📰 **每日战报**：HLTV 每日要闻速递，掌握全球 CS2 赛事动态
- 📈 **减量市场分析**：深度分析 CS2 饰品市场的减量趋势和投资机会
- 💎 **价值投资研报**：提供专业的饰品投资研究报告

## 🛠️ 技术栈

- **静态站点生成器**：Hexo
- **主题**：Cactus
- **前端**：
  - Stylus (63.5%)
  - EJS (18.1%)
  - JavaScript (9.7%)
  - CSS (1.2%)
- **自动化脚本**：Python (7.5%)
- **部署**：GitHub Pages / GitHub Actions

## 🚀 快速开始

### 前置要求

- Node.js (v12.0 或更高版本)
- npm 或 yarn
- Git

### 安装步骤

1. **克隆仓库**

```bash
git clone https://github.com/ChuheLin/cs2-wang.git
cd cs2-wang
```

2. **安装依赖**

```bash
npm install
```

3. **本地预览**

```bash
hexo server
```

访问 `http://localhost:4000` 查看网站

4. **生成静态文件**

```bash
hexo generate
```

5. **部署**

```bash
hexo deploy
```

## 📝 内容创建

### 创建新文章

```bash
hexo new post "文章标题"
```

### 文章模板

文章位于 `source/_posts/` 目录下，使用 Markdown 格式编写。

示例：

```markdown
---
title: 2025-12-06 全市场量化扫描
date: 2025-12-06
tags: [量化分析, 市场扫描]
---

文章内容...
```

## 📂 项目结构

```
cs2-wang/
├── .github/              # GitHub Actions 配置
├── scaffolds/            # 文章模板
├── scripts_auto/         # 自动化脚本
├── source/               # 源文件
│   ├── _posts/          # 博客文章
│   └── images/          # 图片资源
├── themes/               # 主题文件
│   └── cactus/          # Cactus 主题
├── _config.yml          # Hexo 配置文件
├── _config.cactus.yml   # Cactus 主题配置
└── package.json         # 项目依赖
```

## 🤖 自动化功能

本项目使用 GitHub Actions 实现自动化部署和内容更新。每次推送到主分支时，将自动：

1. 生成静态网站
2. 部署到 GitHub Pages
3. 运行自动化分析脚本（如有配置）

## 🎨 自定义配置

### 修改网站配置

编辑 `_config.yml` 文件：

```yaml
# 网站
title: CS2.wang
subtitle: 专注饰品价值投资组合
description: CS饰品价值投资教父
author: Your Name
language: zh-CN
timezone: Asia/Shanghai
```

### 修改主题配置

编辑 `_config.cactus.yml` 文件来自定义 Cactus 主题的外观和功能。

## 📊 内容类型

### 1. 每日战报

- HLTV 赛事要闻
- 战队动态
- 比赛分析

### 2. 量化报告

- 市场数据分析
- 价格趋势预测
- 投资机会识别

### 3. 研究报告

- 饰品市场深度分析
- 减量市场研究
- 投资策略建议

## 🤝 贡献指南

欢迎对本项目做出贡献！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🔗 相关链接

- **网站**：[cs2.wang](https://cs2.wang)
- **GitHub**：[ChuheLin/cs2-wang](https://github.com/ChuheLin/cs2-wang)
- **作者主页**：[GitHub Profile](https://github.com/ChuheLin)

## 📮 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 提交 [Issue](https://github.com/ChuheLin/cs2-wang/issues)
- 访问网站留言

## ⚠️ 免责声明

本网站提供的所有投资分析和建议仅供参考，不构成投资建议。CS2 饰品市场存在风险，投资需谨慎。请根据自身情况做出独立判断。

---

**由 Gemini 创建 | DeepSeek 运营**

_专注 CS2 饰品投资 | 在这里找到价值_
