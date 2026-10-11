param([string]$LibraryRoot = '.tools/tom/lib/net8.0')
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path $PSScriptRoot -Parent
$taskLibrary = Join-Path $taskRoot $LibraryRoot
Add-Type -Path (Join-Path $taskLibrary 'Microsoft.AnalysisServices.Core.dll')
Add-Type -Path (Join-Path $taskLibrary 'Microsoft.AnalysisServices.Tabular.dll')
$taskDefinition = Join-Path $taskRoot 'powerbi/vibe_dashboarding_test/vibe_dashboarding_test.SemanticModel/definition'
$taskDatabase = [Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder($taskDefinition)
if ($taskDatabase.Model.Tables.Count -ne 5 -or $taskDatabase.Model.Relationships.Count -ne 4) { throw 'Unexpected model structure' }
foreach ($taskRelation in $taskDatabase.Model.Relationships) {
    if ($null -eq $taskRelation.FromColumn -or $null -eq $taskRelation.ToColumn) { throw 'Unresolved model relationship' }
}
# Persist the local fallback through Microsoft's serializer, not a custom metadata tool.
[Microsoft.AnalysisServices.Tabular.TmdlSerializer]::SerializeDatabaseToFolder($taskDatabase, $taskDefinition)
Get-ChildItem -LiteralPath $taskDefinition -Filter '*.tmdl' -Recurse | ForEach-Object {
    $taskText = [IO.File]::ReadAllText($_.FullName).TrimEnd() + "`n"
    [IO.File]::WriteAllText($_.FullName, $taskText, [Text.UTF8Encoding]::new($false))
}
$taskResult = @{
    status = 'PASS'
    library = 'Microsoft.AnalysisServices 19.118.3'
    check = 'TMDL deserialize, resolve relationship references and serialize through TOM'
    tables = $taskDatabase.Model.Tables.Count
    relationships = $taskDatabase.Model.Relationships.Count
    measures = @($taskDatabase.Model.Tables | ForEach-Object { $_.Measures }).Count
    dax_engine = 'NOT VERIFIED'
    import_refresh = 'NOT VERIFIED'
}
$taskResult | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 -LiteralPath (Join-Path $taskRoot 'docs/vibe_dashboarding_test/tmdl_validation.json')
$taskResult | ConvertTo-Json -Depth 8
