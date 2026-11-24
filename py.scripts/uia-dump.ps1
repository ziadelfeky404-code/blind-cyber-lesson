param([int]$MaxDepth = 4, [int]$MaxNodes = 400)

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$script:Patterns = @{
    'Invoke'    = [System.Windows.Automation.InvokePattern]::Pattern
    'Toggle'    = [System.Windows.Automation.TogglePattern]::Pattern
    'Expand'    = [System.Windows.Automation.ExpandCollapsePattern]::Pattern
    'SelectItem'= [System.Windows.Automation.SelectionItemPattern]::Pattern
    'Value'     = [System.Windows.Automation.ValuePattern]::Pattern
    'Scroll'    = [System.Windows.Automation.ScrollPattern]::Pattern
    'RangeValue'= [System.Windows.Automation.RangeValuePattern]::Pattern
    'Selection' = [System.Windows.Automation.SelectionPattern]::Pattern
}

$root = [System.Windows.Automation.AutomationElement]::RootElement
$top = $root.FindAll([System.Windows.Automation.TreeScope]::Children,
    [System.Windows.Automation.Condition]::TrueCondition)
Write-Output "TOP-LEVEL WINDOWS:"
foreach ($w in $top) {
    Write-Output ("  [{0}] '{1}'" -f $w.Current.ControlType.ProgrammaticName.Replace('ControlType.',''), $w.Current.Name)
}

$win = $null
foreach ($w in $top) {
    if ($w.Current.Name -like 'Articulate Storyline*') { $win = $w; break }
}
if (-not $win) { Write-Output "STORYLINE WINDOW NOT FOUND"; exit 1 }
Write-Output "--- TREE ---"

$script:count = 0
function Walk($el, $depth) {
    if ($depth -gt $MaxDepth -or $script:count -ge $MaxNodes) { return }
    $script:count++
    $ci = $el.Current
    $pats = @()
    foreach ($k in $script:Patterns.Keys) {
        $obj = $null
        try { if ($el.TryGetCurrentPattern($script:Patterns[$k], [ref]$obj)) { $pats += $k } } catch {}
    }
    $name = "$($ci.Name)"
    if ($name.Length -gt 55) { $name = $name.Substring(0,55) }
    $indent = '  ' * $depth
    Write-Output ("{0}[{1}] '{2}' auto='{3}' pats={4}" -f $indent, $ci.ControlType.ProgrammaticName.Replace('ControlType.',''), $name, $ci.AutomationId, ($pats -join ','))
    if ($depth -lt $MaxDepth -and $script:count -lt $MaxNodes) {
        $walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker
        $child = $walker.GetFirstChild($el)
        while ($child -and $script:count -lt $MaxNodes) {
            Walk $child ($depth + 1)
            $child = $walker.GetNextSibling($child)
        }
    }
}
Walk $win 0
Write-Output "TOTAL NODES VISITED: $($script:count)"
