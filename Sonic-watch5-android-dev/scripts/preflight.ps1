[CmdletBinding()]
param(
    [string]$Workspace = 'E:/Code/Sonic/watch5',
    [ValidateSet('ui', 'ble', 'port', 'docs')]
    [string]$Profile = 'ui',
    [string]$Jdk = 'D:/Scoop/apps/OracleJDK17/current',
    [string]$BuildTools,
    [string]$PlatformJar,
    [string]$AdbPath
)

# 仅检查路径存在：不联网、不启动子进程或 ADB、不写文件、不读取凭据。
$ErrorActionPreference = 'Stop'
$workspacePath = [IO.Path]::GetFullPath($Workspace)
if (!$BuildTools) { $BuildTools = Join-Path $workspacePath 'tesla-watch/probe/.tools/build-tools/android-15' }
if (!$PlatformJar) { $PlatformJar = Join-Path $workspacePath 'tesla-watch/probe/.tools/platform/android-35/android.jar' }
$checks = [Collections.Generic.List[object]]::new()
function Add-PathCheck([string]$Category, [string]$Name, [string]$Path, [bool]$Required = $true) {
    $present = $false
    if ($Path) { $present = Test-Path -LiteralPath $Path -PathType Leaf }
    $checks.Add([pscustomobject]@{
        category = $Category; name = $Name; path = $Path
        present = [bool]$present; required = $Required
    })
}
foreach ($name in @('AGENTS.md', 'Agent.md', 'WATCH5_DEVELOPMENT.md', 'WATCH5_AGENT_QUICKSTART.md', 'WATCH5_ENGINEERING_GUIDE.md', 'docs/watch5/PROJECT_TEMPLATE.md')) {
    Add-PathCheck 'knowledge' $name (Join-Path $workspacePath $name)
}

if ($Profile -ne 'docs') {
    foreach ($tool in @('java', 'javac', 'jar', 'keytool')) {
        Add-PathCheck 'build-tool' $tool (Join-Path $Jdk "bin/$tool.exe")
    }
    Add-PathCheck 'build-tool' 'android.jar' $PlatformJar
    foreach ($tool in @('aapt2.exe', 'zipalign.exe', 'lib/d8.jar', 'lib/apksigner.jar')) {
        Add-PathCheck 'build-tool' $tool (Join-Path $BuildTools $tool)
    }
    if (!$AdbPath) {
        $adbCommand = Get-Command adb -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($adbCommand) { $AdbPath = $adbCommand.Source }
    }
    # 离线构建不强制要求 ADB；不执行它，也不启动其服务。
    Add-PathCheck 'device-tool' 'adb' $AdbPath $false
    # 只检查签名文件是否存在，不加载或导出签名密钥。
    Add-PathCheck 'signing' 'existing-development-key' (Join-Path $workspacePath 'tesla-watch/probe/.tools/debug.keystore') $false
}

$referenceFiles = switch ($Profile) {
    'ui' { @('tesla-watch/preview-apk/build.ps1', 'tesla-watch/preview-apk/AndroidManifest.xml', 'tesla-watch/preview-apk/src/cn/sonic/teslapreview/MainActivity.java') }
    'ble' { @('tesla-watch/ble-app/README.md', 'tesla-watch/ble-app/build.ps1', 'tesla-watch/ble-app/test.ps1', 'tesla-watch/probe/TEST_GUIDE.md') }
    'port' { @('watch/analysis/ninebot-rea/build-compat.ps1', 'watch/analysis/ninebot-rea/COMPATIBILITY_RESULT.md', 'watch/analysis/ninebot-phone/bridge-probe/SESSION_2026-11-05.md') }
    'docs' { @('README.md') }
}
foreach ($file in $referenceFiles) { Add-PathCheck 'reference' $file (Join-Path $workspacePath $file) }
$missingRequired = @($checks | Where-Object { $_.required -and !$_.present })
$missingOptional = @($checks | Where-Object { !$_.required -and !$_.present })
[ordered]@{
    schema_version = 1
    checked_at = [DateTimeOffset]::Now.ToString('o')
    workspace = $workspacePath
    profile = $Profile
    status = $(if ($missingRequired.Count) { 'missing_required_paths' } else { 'paths_present' })
    status_message = $(if ($missingRequired.Count) { '缺少必需路径，请检查缺失项。' } else { '所需路径已找到，尚未执行工具或验证设备。' })
    scope = '仅检查本地路径存在；未执行工具、查询设备、构建或验证运行结果。'
    documented_device = @{
        evidence_date = '2026-11-04/05'; source = 'WATCH5_DEVELOPMENT.md（历史基线，本次未查询设备）'
        model = 'M2505W1'; api = 34; pixels = '480x480'; density_dpi = 320; nominal_dp = '240x240'; abi = @('armeabi-v7a', 'armeabi')
    }
    checks = @($checks.ToArray())
    missing_required = @($missingRequired | ForEach-Object name)
    missing_optional = @($missingOptional | ForEach-Object name)
    next_step = $(if ($missingRequired.Count) { '检查指定路径和覆盖参数；不要重新下载全部工具，也不要据此判断手表离线。' } else { '读取项目当前状态，只运行与本次任务相关的构建和测试流程。' })
} | ConvertTo-Json -Depth 6
if ($missingRequired.Count) { exit 1 }
exit 0
