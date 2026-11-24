param([Parameter(Mandatory=$true)][string]$Name)
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class M {
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, IntPtr extra);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
}
"@

$root = [System.Windows.Automation.AutomationElement]::RootElement
$top = $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
$win = $null
foreach ($w in $top) { if ($w.Current.Name -like 'Articulate Storyline*') { $win = $w; break } }
if (-not $win) { Write-Output 'NO STORYLINE WINDOW'; exit 1 }
[void][M]::SetForegroundWindow($win.Current.NativeWindowHandle)
Start-Sleep -Milliseconds 500

$cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $Name)
$el = $win.FindFirst([System.Windows.Automation.TreeScope]::Subtree, $cond)
if (-not $el) { Write-Output "ELEMENT NOT FOUND: $Name"; exit 1 }
$r = $el.Current.BoundingRectangle
$cx = [int]($r.X + $r.Width / 2)
$cy = [int]($r.Y + $r.Height / 2)
Write-Output "clicking '$Name' at $cx,$cy"
[void][M]::SetCursorPos($cx, $cy)
[M]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
Start-Sleep -Milliseconds 60
[M]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
Start-Sleep -Seconds 2

Write-Output "--- top-level windows ---"
$top2 = $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
foreach ($w in $top2) { $n = $w.Current.Name; if ($n -and $n -notmatch 'Program Manager') { Write-Output ("  [{0}] '{1}'" -f $w.Current.ControlType.ProgrammaticName.Replace('ControlType.',''), $n) } }

Write-Output "--- named elements in Storyline subtree ---"
$all = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
$c = 0
foreach ($e in $all) {
    $n = $e.Current.Name
    if ($n) { Write-Output ("  '{0}'  auto={1}" -f $n, $e.Current.AutomationId); $c++ }
    if ($c -ge 40) { break }
}
