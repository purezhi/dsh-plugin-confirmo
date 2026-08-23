# 提交插件到 DSH 插件市场

本文说明如何把 dsh 插件提交到 DSH 内置的**社区插件市场**（`dsh-community-market`，即 Desktop「设置 → 插件 → 插件市场」）。
以本仓库 `dsh-plugin-confirmo` 的提交过程为例。

## 市场机制简介

DSH Community Market 本身**不维护插件目录**，它是一个「壳」：只负责展示、搜索与托管安装，数据来自外部的**目录来源（catalog source）**。
因此「提交插件」= 让插件出现在某个目录来源中。目前有三条途径：

| 途径 | 收录方式 | 是否需要审核 | 备注 |
|---|---|---|---|
| **DSH 1024Store**（deepseek1024.com） | GitHub PR 新增一个 JSON 文件 | 机器人静态校验，通过即自动合并 | 官方主要合作目录，全自动 |
| **dshfind**（dshfind.com） | 给仓库加 `dsh-plugin` topic，自动同步 | 无人工 | 每天 02:17 UTC 同步，仅浏览不可安装 |
| **标准来源（自定义）** | 自建 manifest + JSON 接口，用户手动添加 | 无 | 完全开放，需用户填 URL |

> 收录 ≠ 官方审核。所有目录数据都是远程不可信输入，收录只表示提供方返回了元数据，
> 不代表 Anywhere Labs 审核、推荐或保证该插件。安装后插件以用户权限作为本地代码运行。

---

## 路线 1：提交到 DSH 1024Store（推荐，官方主目录）

由 GitHub 仓库 [imsai-sh/awesome-deepseek-harness-plugins](https://github.com/imsai-sh/awesome-deepseek-harness-plugins)
驱动，合并后自动同步到 [deepseek1024.com](https://deepseek1024.com/) 与市场内置的 1024Store 来源。

### 前置条件（在插件仓库内完成）

1. **`package.json` 声明 `dsh.bundle.patch`**，指向仓库内已提交的 patch 文件：

   ```json
   {
     "dsh": {
       "bundle": { "patch": "./cordis.patch.yml" },
       "client": { "inject": [], "platform": "web" }
     }
   }
   ```

   `cordis.patch.yml` 内容即插件注册段（本插件）：

   ```yaml
   - insert:
       - id: confirmo
         name: dsh-plugin-confirmo
   ```

   上游静态校验会检查：patch 字段非空、patch 文件在同一提交中存在。**缺失会直接拒绝 PR。**

2. **`package.json` 声明 `repository`**（指向 GitHub 仓库，为后续 npm 发布/回链校验做准备）：

   ```json
   "repository": { "type": "git", "url": "https://github.com/purezhi/dsh-plugin-confirmo" }
   ```

3. **仓库添加 `dsh-plugin` GitHub topic**（同时满足 dshfind 自动发现）：

   ```bash
   gh repo edit <owner>/<repo> --add-topic dsh-plugin
   ```

4. **入口文件已提交**：上游会检查 `main` / `exports["."]` 指向的文件是否在仓库中。
   构建产物（如 `lib/client.js`）必须提交，否则 GitHub 安装方式会标记为 UNVERIFIED（不阻止收录）。

### 提交步骤

1. fork [imsai-sh/awesome-deepseek-harness-plugins](https://github.com/imsai-sh/awesome-deepseek-harness-plugins)
2. 新增 `catalog/plugins/<owner>--<repo>.json`（文件名规则：id 各段转小写、非字母数字转 `-`、`/` 转 `--`）：

   ```json
   {
     "$schema": "../schema/plugin.schema.json",
     "id": "purezhi/dsh-plugin-confirmo",
     "name": "dsh-plugin-confirmo",
     "repository": "https://github.com/purezhi/dsh-plugin-confirmo",
     "category": "ui",
     "description": {
       "en": "A confirmo.love-style desktop pet for the DSH Web UI with community sprite support.",
       "zh": "在 DSH Web UI 里放一只 Confirmo 桌宠，支持社区精灵图。"
     },
     "added": "2026-08-23"
   }
   ```

   - 分类必须来自 `catalog/categories.json`（当前有：`ui, theme, session, memory, tools, skill, workflow, notify, model, dev, fun`）
   - `repository` 必须等于 `https://github.com/<id>`，`added` 为提交日期
3. **PR 只允许新增这一个 JSON 文件**，不得改动其他路径（README 等由机器人自动生成）
4. 机器人 `static-review` 自动校验：
   - JSON 字段/文件名/分类/描述/日期
   - 通过 GitHub API 读取插件仓库：`dsh.bundle.patch` 声明、patch 文件存在、入口文件已提交
   - 校验通过 → 自动 squash-merge（新增单条目）；修改/删除条目需人工审核
5. 合并后 CI 自动同步到 `deepseek1024.com` 生产目录，无需人工操作

### 本插件的提交记录

- PR: https://github.com/imsai-sh/awesome-deepseek-harness-plugins/pull/174（已合并）
- 投稿文件: `docs/submission/purezhi--dsh-plugin-confirmo.json`
- 合并后 `Catalog sync` workflow 会推送目录到 deepseek1024.com（同步为异步排队，稍候可见）

### （可选）让插件进入市场「可安装」标签页

市场托管安装要求 npm 包，且满足 fail-closed 校验：

- 发布到 npm（精确稳定版本，如 `1.0.0`）
- `package.json` 的 `repository.url` 与目录中的仓库 URL 完全一致（`repository_backlink` 回链校验）
- 包内 `dsh.bundle.patch` 指向的 patch 存在
- 无 `preinstall` / `install` / `postinstall` / `prepare` 生命周期脚本
- 未被产品 blocklist 收录

不发布 npm 也能被收录，只是安装方式标记为 GitHub 安装。

---

## 路线 2：提交到 dshfind（零成本）

[dshfind](https://dshfind.com)（[源码](https://github.com/hikariming/dshfind)）直接从 GitHub `dsh-plugin` topic 自动收集：

1. 给公开仓库添加 `dsh-plugin` topic（见上）
2. 等待每日同步（02:17 UTC），约一天内出现
3. 两个同步周期后仍未出现 → 开 issue 询问（可能被判定 off-topic，或仓库非公开/已归档）

注意：dshfind 当前不提供精确 npm 版本，条目**仅可浏览**，不会出现在市场「可安装」标签页。

---

## 路线 3：自建标准来源（完全开放）

任何个人/社区都可以发布符合 [catalog-provider-contract](https://github.com/deepseek-ai/deepseek-harness) 的目录：

1. 发布一份静态 manifest（`catalog-source` schema）：

   ```json
   {
     "manifestVersion": "1.0.0",
     "providerId": "org.example.community-catalog",
     "name": "Example Community Catalog",
     "attribution": { "name": "Example Plugin Community", "url": "https://plugins.example.org/" },
     "transport": { "kind": "https-json", "endpoint": "https://plugins.example.org/v1/plugins", "method": "GET" },
     "query": { "supported": ["q", "category", "cursor", "limit"], "defaultLimit": 50, "maxLimit": 50, "sorts": [] }
   }
   ```

2. 实现 `GET /v1/plugins`，返回 `catalog-provider-page` 格式 JSON（`schemaVersion: "1.0.0"` + `items` 数组）
3. 用户在市场的「来源」视图填写 manifest URL 即可添加

零审批、零合作，但需要用户手动添加 URL，不会默认出现在所有人面前。已有格式不同的公开 API
也可以联系市场维护者，通过随市场发布的**受审 adapter** 作为合作数据源接入。

---

## 常见问题

**Q: 提交后多久能在市场看到？**
1024Store：PR 自动合并后由 `Catalog sync` workflow 推送，异步排队，通常几分钟到几十分钟。
dshfind：topic 每日同步，约一天。

**Q: 收录后插件会被审核安全吗？**
不会。市场只做静态结构校验（patch 声明、文件存在），不安装、不构建、不执行第三方代码。
安装前请自行检查插件行为。

**Q: 市场里的安装命令是官方执行的吗？**
不是。市场展示的 npm/GitHub 命令只供用户参考，由用户在终端自行执行；
「可安装」标签页的托管安装才由 Desktop 受管服务执行（仅接受精确稳定 npm 版本 + 回链校验）。

**Q: 想出现在多个目录？**
可以。1024Store（PR）、dshfind（topic）互不冲突，可同时收录；自建标准来源任意添加。

---

## 参考

- 市场文档: `~/.dsh/profiles/node_modules/dsh-community-market/docs/`（install-and-uninstall / catalog-provider-contract / catalog-adapter-guide）
- 1024Store 贡献指南: https://github.com/imsai-sh/awesome-deepseek-harness-plugins/blob/main/CONTRIBUTING.md
- dshfind: https://dshfind.com · https://github.com/hikariming/dshfind
