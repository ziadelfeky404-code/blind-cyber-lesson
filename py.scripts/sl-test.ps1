Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
}
"@
Add-Type -AssemblyName System.Windows.Forms

$p = Get-Process Storyline -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $p) { Write-Output 'Storyline not running'; exit }
$h = $p.MainWindowHandle
[Win32]::ShowWindow($h, 3) | Out-Null
[Win32]::SetForegroundWindow($h) | Out-Null
Start-Sleep -Milliseconds 800

function TopWindows {
    $root = [System.Windows.Automation.AutomationElement]::RootElement
    $top = $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
    $res = @()
    foreach ($w in $top) { $res += ("[{0}] '{1}'" -f $w.Current.ControlType.ProgrammaticName.Replace('ControlType.',''), $w.Current.Name) }
    return $res
}

Write-Output "BEFORE:"; TopWindows | ForEach-Object { Write-Output "  $_" }

Write-Output "Sending Ctrl+Shift+S ..."
[System.Windows.Forms.SendKeys]::SendWait("^+s")
Start-Sleep -Seconds 3

Write-Output "AFTER:"; TopWindows | ForEach-Object { Write-Output "  $_" }
Write-Output "Foreground now: $([Win32]::GetForegroundWindow())  Storyline HWND: $h"
