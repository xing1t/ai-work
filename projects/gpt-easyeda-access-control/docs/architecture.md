# 接入架构与环境

历史记录来源：[交接第 2 节](original/PROJECT_HANDOFF.md)。下表为交接记录，不是本次重新检测的软件安装状态。

```text
Codex → 本机 Python/PowerShell → HTTP bridge
      → WebSocket → Run API Gateway → eda.* API
```

|环境|历史记录与待确认项|
|---|---|
|Windows / PowerShell|系统详细版本待确认；PowerShell 7.6.5|
|EDA 专业版|源 editVersion=3.2.116；About 与 Gateway 扩展版本待确认|
|Python / Node|3.14.4（C:/msys64/mingw64/bin/python.exe）；v26.13.0|
|Git|2.56.0.windows.2（本次命令亦确认）|
|easyeda-api skill|本机 .cline/skills/easyeda-api，历史版本 1.1.28；不据路径推断当前客户端为 Cline|
|布线计算|Freerouting 2.5.0 + Temurin JRE 25.0.5+8|
|几何计算|Node + clipper-lib 6.4.2|

bridge 历史地址为 http://127.0.0.1:49620；health 读状态，execute 可执行 EDA JavaScript。此次未访问端口，也未启动或检查桥服务。交接时活动页是原理图 p1；当前活动页未知，不假定为 PCB3。目标 UUID 仅为历史定位信息，不是授权或当前目标确认。

完整本机路径和工程/库标识为保持原始证据而保留；它们不是凭据，但公开前仍需决定披露范围。依赖版本、来源及授权见 [参考表](../references/README.md)。
