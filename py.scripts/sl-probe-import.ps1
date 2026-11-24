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

function Click-Element($el) {
    $r = $el.Current.BoundingRectangle
    $cx = [int]($r.X + $r.Width / 2)
    $cy = [int]($r.Y + $r.Height / 2)
    [void][M]::SetCursorPos($cx, $cy)
    [M]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 60
    [M]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
    Write-Output "  clicked '$($el.Current.Name)' at $cx,$cy"
}

function Find-ByName($rootEl, $name) {
    $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $name)
    return $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
}

# Kill and relaunch to get the start screen
Get-Process Storyline -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 4
Start-Process "C:\Program Files (x86)\Articulate\Storyline 3\Storyline.exe"
Write-Output "waiting for start screen..."
$deadline = (Get-Date).AddSeconds(90)
do {
    Start-Sleep -Seconds 3
    $top = $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
    $win = $null
    foreach ($w in $top) { if ($w.Current.Name -eq 'Articulate Storyline') { $win = $w; break } }
} while (-not $win -and (Get-Date) -lt $deadline)

if (-not $win) { Write-Output 'start screen not found'; exit 1 }
Write-Output 'start screen ready'

$imp = $win.FindFirst([System.Windows.Automation.TreeScope]::Descendants, (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, 'Import')))
if (-not $imp) { Write-Output 'Import not found'; exit 1 }
Click-Element $imp
Start-Sleep -Seconds 2

Write-Output '--- ALL named elements across desktop (post-Import) ---'
$all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
$c = 0
foreach ($e in $all) {
    $n = $e.Current.Name
    if ($n -and $n.Length -lt 40) {
        $t = $e.Current.ControlType.ProgrammaticName.Replace('ControlType.','')
        Write-Output ("  [{0}] '{1}' auto={2}" -f $t, $n, $e.Current.AutomationId)
        $c++
    }
    if ($c -ge 60) { break }
}
