# 归档与核验

- [输入统计](intake-summary.json)：192 个项目文件、7 个外部引用；另加入清单自身。
- [完整归档映射](archive-map.json)：每个条目的原路径、仓库路径、原清单哈希、实际源及复制哈希、用途、分类、差异及排除/重复关系。
- [工程快照离线结果](offline-evidence-check.json)：PCB 计数、初始基准、原理图 173 连接与换行差异。
- [本地检查报告](local-check-report.json)：检查器结果，非活动 EDA 检查。
- [只读检查器](verify_archive.py)：Python 标准库，仓库根运行 `python projects/gpt-easyeda-access-control/validation/verify_archive.py`；无网络，无 EDA 调用，不写文件。

所有复制证据保留原始字节，没有脱敏副本；清单自身未列自身哈希，因此映射 manifest_sha256=null，不伪造。不同换行对应不同哈希。排除临时日志、覆盖回包、多数旧中间产物；重复关系由实际哈希识别。外部引用仅检查、不复制。

隐私与许可：原证据保留个人本机路径、工程及库标识；它们不是认证凭据，尚未发布。公开前需决定披露及第三方资源范围，如脱敏必须另存并重新记录映射，不覆盖本地原证据。
