Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$root = [System.Windows.Automation.AutomationElement]::RootElement
$top = $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
$win = $null
foreach ($w in $top) { if ($w.Current.Name -like 'Articulate Storyline*') { $win = $w; break } }
if (-not $win) { Write-Output 'NO WIN'; exit }

$names = @('Button','Edit','MenuItem','MenuBar','TabItem','ListItem','ComboBox','Hyperlink','Text','TreeItem','CheckBox')
foreach ($n in $names) {
    $ct = [System.Windows.Automation.ControlType]::$n
    $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, $ct)
    $all = $win.FindAll([System.Windows.Automation.TreeScope]::Subtree, $c)
    Write-Output ("{0} = {1}" -f $n, $all.Count)
    if ($n -in @('Button','TabItem','MenuItem') -and $all.Count -gt 0) {
        $i = 0
        foreach ($e in $all) {
            if ($i -ge 15) { break }
            Write-Output ("    '{0}'" -f $e.Current.Name)
            $i++
        }
    }
}
