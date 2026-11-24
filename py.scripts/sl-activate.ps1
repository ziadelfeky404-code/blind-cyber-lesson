param([Parameter(Mandatory=$true)][string]$Name)
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms

$root = [System.Windows.Automation.AutomationElement]::RootElement
$top = $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
$win = $null
foreach ($w in $top) { if ($w.Current.Name -like 'Articulate Storyline*') { $win = $w; break } }
if (-not $win) { Write-Output 'NO STORYLINE WINDOW'; exit 1 }

$cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $Name)
$el = $win.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
if (-not $el) { Write-Output "NOT FOUND: $Name"; exit 1 }

$el.SetFocus()
Start-Sleep -Milliseconds 300
Write-Output "has focus: $($el.Current.HasKeyboardFocus)"
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Seconds 2

Write-Output "--- named elements after ---"
$all = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
$c = 0
foreach ($e in $all) { $n = $e.Current.Name; if ($n) { Write-Output "  '$n' auto=$($e.Current.AutomationId)"; $c++ }; if ($c -ge 40) { break } }
