# 工程资料库

保存设计成果、验证证据、工程经验、历史脚本与后续计划，逐步形成可维护的工程知识。GitHub 目标为公开仓库 `xing1t/ai-work`，接入状态见下方链接；项目暂不添加对外许可证。

- [首个项目：GPT + 嘉立创 EDA 专业版半自动设计密码门禁系统](projects/gpt-easyeda-access-control/README.md)
- [归档映射与输入核验](projects/gpt-easyeda-access-control/validation/README.md)
- [GitHub 接入准备](GITHUB_SETUP.md)
- [维护规则](AGENTS.md)
- [可填写模板](templates/README.md)

添加项目：复制新项目模板到 projects/<project-id>/README.md，按需创建 docs、hardware、validation、scripts/historical、prompts、references。先明确需求、证据和授权，再复制确认过的文件并记录原路径和 SHA-256；更新本页导航。

日常更新：先写本次目标及边界，成果使用新版本名并保存验证证据；将已验证事实、历史记录、计划、待确认项分开。每次提交检查文件清单、差异、凭据和体积，以明确路径暂存。文档更正不覆盖原始证据；需要脱敏时另存副本并记录新哈希。

闲鱼自动化、AI 接单和 AI 漫剧仅为未来方向，尚未立项实现。通用工具成熟后再增加 tools，暂不建设网站、数据库或复杂 CI。
