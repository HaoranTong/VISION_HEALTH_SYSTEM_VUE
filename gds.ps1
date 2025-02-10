# 定义根目录和输出文件路径
$rootDir = "E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM"
$currentDate = Get-Date -Format "yyMMdd"  # 获取当前日期的年月日
$outputPath = "$rootDir\directory_structure_$currentDate.md"  # 在文件名末尾添加日期

# 定义需要排除的目录和文件模式
$excludePatterns = @(
    "node_modules",
    "\.git",
    "__pycache__",
    "\.vscode",
    "\.venv",
    ".*\.tmp$",
    "test_data"
)

# 定义函数：获取目录结构
function Get-DirectoryStructure {
    param (
        [string]$Path,        # 当前路径
        [int]$Level = 0,      # 当前层级（用于缩进）
        [bool]$IsLast = $false, # 是否是最后一个项目
        [string]$Prefix = ""  # 前缀（用于树状结构）
    )

    # 获取目录并排除符号链接
    $dirs = Get-ChildItem -Path $Path -Directory -Force -Attributes !ReparsePoint |
    Where-Object { $_.Name -notmatch ($excludePatterns -join "|") }

    # 获取文件并过滤
    $files = Get-ChildItem -Path $Path -File -Force |
    Where-Object { $_.Name -notmatch ($excludePatterns -join "|") }

    # 处理目录
    $dirIndex = 0
    foreach ($dir in $dirs) {
        $dirIndex++
        $isLastDir = ($dirIndex -eq $dirs.Count) -and ($files.Count -eq 0)
        $currentPrefix = if ($IsLast) { "    " } else { "│   " }

        # 生成树状符号
        if ($Level -eq 0 -and $dirIndex -eq 1) {
            $line = "├── "
        }
        elseif ($dirIndex -eq $dirs.Count + $files.Count) {
            $line = "└── "
        }
        else {
            $line = "├── "
        }

        # 输出目录行
        Write-Output "$Prefix$line📁 $($dir.Name)/"

        # 递归处理子目录
        $newPrefix = if ($IsLast) { "$Prefix    " } else { "$Prefix│   " }
        Get-DirectoryStructure -Path $dir.FullName -Level ($Level + 1) -IsLast $isLastDir -Prefix $newPrefix
    }

    # 处理文件
    $fileIndex = 0
    foreach ($file in $files) {
        $fileIndex++
        $isLastFile = ($fileIndex -eq $files.Count)

        # 生成树状符号
        if ($fileIndex -eq 1 -and $dirs.Count -eq 0) {
            $line = if ($IsLast) { "└── " } else { "├── " }
        }
        else {
            $line = if ($isLastFile) { "└── " } else { "├── " }
        }

        # 输出文件行
        Write-Output "$Prefix$line📄 $($file.Name)"
    }
}

# 执行并生成文件
# 1. 输出文件头部信息
@"
# 开发文档目录结构$currentDate

# 📂 根目录路径
\`\`\`
$rootDir
\`\`\`

# 📁 目录结构
"@ | Out-File -FilePath $outputPath

# 2. 输出目录结构
Get-DirectoryStructure -Path $rootDir | Out-File -FilePath $outputPath -Append

# 提示生成成功
Write-Host "目录结构已生成至 $outputPath" -ForegroundColor Green