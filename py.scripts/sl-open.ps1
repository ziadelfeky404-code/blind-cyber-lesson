param([Parameter(Mandatory=$true)][string]$Path, [int]$Seconds = 90)
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

Start-Process "C:\Program Files (x86)\Articulate\Storyline 3\Storyline.exe" -ArgumentList "`"$Path`""
Write-Output "opened request: $Path"

$deadline = (Get-Date).AddSeconds($Seconds)
$last = ""
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 3
    $t = (Get-Process Storyline -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle } | Select-Object -First 1).MainWindowTitle
    if ($t -and $t -ne $last) { Write-Output ("[{0:HH:mm:ss}] TITLE: {1}" -f (Get-Date), $t); $last = $t }
}
Write-Output "--- top-level windows ---"
$root = [System.Windows.Automation.AutomationElement]::RootElement
$top = $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
foreach ($w in $top) {
    $n = $w.Current.Name
    if ($n -and $n -notmatch 'Program Manager') { Write-Output ("  [{0}] '{1}'" -f $w.Current.ControlType.ProgrammaticName.Replace('ControlType.',''), $n) }
}
