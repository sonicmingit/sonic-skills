# Brother DCP‑T725DW（内部参考，不含密码）

## 已知信息
- Web 管理地址：`http://10.0.0.24/`（内网）
- CUPS 队列：`Brother_T725DW`
- IPP endpoint（通过 `ippfind` 发现）：`ipp://Brother.local:631/ipp/print`
- 端口：80/443/631/515/9100

## 典型命令
- 测试打印：
  ```bash
  echo "test $(date)" | lp -d Brother_T725DW -t "test"
  ```
- 查看队列：`lpstat -o`
- 取消任务：`cancel Brother_T725DW-<JOBID>`
- 清空队列：`cancel -a Brother_T725DW`

## 排障要点
- “无默认目标”：`sudo lpadmin -d Brother_T725DW`
- 队列暂停：`cupsenable Brother_T725DW && cupsaccept Brother_T725DW`
- 看日志：`sudo journalctl -u cups -n 200 --no-pager`
