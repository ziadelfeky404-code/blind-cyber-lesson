Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class M {
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, IntPtr extra);
}
"@
$root = [System.Windows.Automation.AutomationElement]::RootElement

function Click-At($x, $y) {
    [void][M]::SetCursorPos([int]$x, [int]$y)
    [M]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 60
    [M]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
}

$win = $null
$top = $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
foreach ($w in $top) { if ($w.Current.Name -eq 'Articulate Storyline') { $win = $w; break } }
if (-not $win) { Write-Output 'start screen not present'; exit 1 }

$imp = $win.FindFirst([System.Windows.Automation.TreeScope]::Descendants, (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, 'Import')))
$r = $imp.Current.BoundingRectangle
Write-Output "Import rect: $($r.X),$($r.Y) $($r.Width)x$($r.Height)"

Click-At ($r.X + $r.Width/2) ($r.Y + $r.Height/2)
Write-Output "clicked Import; waiting 8s..."
Start-Sleep -Seconds 8

Write-Output "--- top-level windows ---"
$top2 = $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
foreach ($w in $top2) {
    $n = $w.Current.Name
    if ($n -and $n -notmatch 'Program Manager') { Write-Output ("  [{0}] '{1}'" -f $w.Current.ControlType.ProgrammaticName.Replace('ControlType.',''), $n) }
}
