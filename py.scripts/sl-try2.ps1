Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class M2 {
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, IntPtr extra);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
}
"@
$root = [System.Windows.Automation.AutomationElement]::RootElement
function Click-At($x, $y) {
    [void][M2]::SetCursorPos([int]$x, [int]$y)
    [M2]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 70
    [M2]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
}
function Get-Tops {
    $res = @()
    $t = $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
    foreach ($w in $t) { if ($w.Current.Name) { $res += $w.Current.Name } }
    return $res
}

$known = @('Articulate Storyline','OpenCode','media-work')
$win = $null
foreach ($w in $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
    if ($w.Current.Name -eq 'Articulate Storyline') { $win = $w; break }
}
if (-not $win) { Write-Output 'no start screen'; exit 1 }
[void][M2]::ShowWindow([IntPtr]$win.Current.NativeWindowHandle, 3)
[void][M2]::SetForegroundWindow([IntPtr]$win.Current.NativeWindowHandle)
Start-Sleep -Seconds 1
$imp = $win.FindFirst([System.Windows.Automation.TreeScope]::Descendants, (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, 'Import')))
$r = $imp.Current.BoundingRectangle
$cx = [int]($r.X + $r.Width/2); $cy = [int]($r.Y + $r.Height/2)
Write-Output "Import center: $cx,$cy"

foreach ($dy in @(0, 22, 30, 38, 46, 54, 70)) {
    Click-At $cx ($cy + $dy)
    Start-Sleep -Seconds 1
    $tops = Get-Tops
    $new = $tops | Where-Object { $_ -notmatch 'Articulate Storyline|OpenCode|media-work|Brave|Word|YouTube|Task View|System Clock|Action Center|Start|Type here|Program Manager' }
    Write-Output ("dy=$dy  new-windows: {0}" -f (($new -join ' | ')))
    if ($new) { Write-Output "  -> found: $($new -join ' | ')"; break }
}
Write-Output '--- final tops ---'
Get-Tops | ForEach-Object { Write-Output "  $_" }
