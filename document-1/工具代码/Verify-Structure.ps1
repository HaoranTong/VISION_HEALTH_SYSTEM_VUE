# filename: Verify-Structure.ps1
$requiredDirs = @(
    "src/context_system/api",
    "src/context_system/core/services",
    "frontend/vscode-extension/src",
    "config/app",
    "tests/e2e"
)

foreach ($dir in $requiredDirs) {
    if (-not (Test-Path $dir)) {
        Write-Host "[错误] 缺失目录: $dir" -ForegroundColor Red
        exit 1
    }
}

Write-Host "[验证通过] 目录结构符合规范" -ForegroundColor Green