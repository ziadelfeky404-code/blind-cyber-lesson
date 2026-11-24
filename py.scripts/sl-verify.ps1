param([Parameter(Mandatory=$true)][string]$Path)
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$root = [System.Windows.Automation.AutomationElement]::RootElement

Get-Process Storyline -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

$tmp = "C:\Users\ZIADEL~1\AppData\Local\Temp\opencode\course-test.story"
Copy-Item -LiteralPath $Path -Destination $tmp -Force
Write-Output ("launching: " + $tmp)
Start-Process -FilePath "C:\Program Files (x86)\Articulate\Storyline 3\Storyline.exe" -ArgumentList ('"' + $tmp + '"')

$deadline = (Get-Date).AddSeconds(120)
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 3
    $t = $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
    foreach ($w in $t) {
        $n = $w.Current.Name
        if ($n -and ($n -like "Articulate Storyline*" -or $n -match "Error|Import|Problem|corrupt|invalid")) {
            $type = $w.Current.ControlType.ProgrammaticName
            Write-Output ("  " + $type + " :: " + $n)
        }
    }
}
