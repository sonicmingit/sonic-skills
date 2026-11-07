#!/bin/bash
# sonic-svc-printer-status 状态获取脚本
# 用法: bash report.sh

WORKSPACE="/home/sonic/openclaw-workspaces/hass"
mkdir -p "$WORKSPACE"

# 读取 HA Token
TOKEN=$(grep -A2 "homeassistant:" "$HOME/openclaw/secrets.yaml" | grep token | awk -F'"' '{print $2}')
HOST="http://10.0.0.88:8124"

if [ -z "$TOKEN" ]; then
  echo "ERROR: 无法从 secrets.yaml 获取 HA token"
  exit 1
fi

# 通用查询函数
query_state() {
  local entity=$1
  curl -s -H "Authorization: Bearer $TOKEN" "$HOST/api/states/$entity" | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)
    print(d.get('state','unavailable'))
except:
    print('error')
"
}

# ============ H2C ============
H2C_PROGRESS=$(query_state "sensor.h2c_31b8dp5c0700638_print_progress")
H2C_REMAINING=$(query_state "sensor.h2c_31b8dp5c0700638_remaining_time")
H2C_LAYER=$(query_state "sensor.h2c_31b8dp5c0700638_current_layer")
H2C_NOZZLE=$(query_state "sensor.h2c_31b8dp5c0700638_nozzle_temperature")
H2C_BED=$(query_state "sensor.h2c_31b8dp5c0700638_bed_temperature")

# 判断H2C是否在打印
H2C_PRINTING=0
if [ "$H2C_PROGRESS" != "error" ] && [ "$H2C_PROGRESS" != "unavailable" ] && [ "$(echo "$H2C_PROGRESS > 0" | bc 2>/dev/null || echo 0)" = "1" ]; then
  H2C_PRINTING=1
fi

# ============ A1Mini ============
A1_ONLINE=$(query_state "binary_sensor.bambu_a1mini_online")
A1_STAGE=$(query_state "sensor.bambu_a1mini_current_stage")
A1_PROGRESS=$(query_state "sensor.bambu_a1mini_print_progress")
A1_NOZZLE=$(query_state "sensor.bambu_a1mini_nozzle_temperature")
A1_BED=$(query_state "sensor.bambu_a1mini_bed_temperature")

A1_PRINTING=0
if [ "$A1_PROGRESS" != "error" ] && [ "$A1_PROGRESS" != "unavailable" ] && [ "$A1_STAGE" != "idle" ]; then
  A1_PRINTING=1
fi

# ============ 下载摄像头图片 ============
H2C_IMAGE=""
A1_IMAGE=""

if [ "$H2C_PRINTING" = "1" ]; then
  curl -s -H "Authorization: Bearer $TOKEN" "$HOST/api/camera_proxy/camera.h2c_31b8dp5c0700638_camera" -o "$WORKSPACE/printer_h2c.jpg"
  H2C_IMAGE="$WORKSPACE/printer_h2c.jpg"
fi

if [ "$A1_PRINTING" = "1" ]; then
  curl -s -H "Authorization: Bearer $TOKEN" "$HOST/api/camera_proxy/camera.bambu_a1mini_camera" -o "$WORKSPACE/printer_a1mini.jpg"
  A1_IMAGE="$WORKSPACE/printer_a1mini.jpg"
fi

# ============ 输出 JSON 汇总 ============
CLEANUP_FILES=""
[ -n "$H2C_IMAGE" ] && CLEANUP_FILES="$H2C_IMAGE"
[ -n "$A1_IMAGE" ] && [ -n "$CLEANUP_FILES" ] && CLEANUP_FILES="$CLEANUP_FILES $A1_IMAGE"
[ -z "$CLEANUP_FILES" ] && CLEANUP_FILES="(无)"

python3 -c "
import json
cleanup = '$CLEANUP_FILES'
result = {
    'h2c': {
        'printing': $H2C_PRINTING,
        'progress': '$H2C_PROGRESS',
        'remaining_min': '$H2C_REMAINING',
        'layer': '$H2C_LAYER',
        'nozzle_temp': '$H2C_NOZZLE',
        'bed_temp': '$H2C_BED',
        'image': '$H2C_IMAGE' if $H2C_PRINTING else None
    },
    'a1mini': {
        'online': '$A1_ONLINE',
        'stage': '$A1_STAGE',
        'printing': $A1_PRINTING,
        'progress': '$A1_PROGRESS',
        'nozzle_temp': '$A1_NOZZLE',
        'bed_temp': '$A1_BED',
        'image': '$A1_IMAGE' if $A1_PRINTING else None
    },
    '_cleanup': cleanup
}
print(json.dumps(result, indent=2, ensure_ascii=False))
"
