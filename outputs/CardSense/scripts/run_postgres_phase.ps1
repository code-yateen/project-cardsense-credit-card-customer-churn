$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$pgBin = Join-Path $root '.pg_runtime\Library\bin'
$pgData = Join-Path $root '.pgdata'
$pgLog = Join-Path $root '.pg_runtime\postgres.log'
$envFile = Join-Path $root '.env'
$dbName = 'cardsense_db'

foreach ($tool in @('initdb.exe', 'pg_ctl.exe', 'psql.exe', 'createdb.exe')) {
    if (-not (Test-Path -LiteralPath (Join-Path $pgBin $tool))) {
        throw "Missing PostgreSQL tool: $(Join-Path $pgBin $tool). Reinstall the project-local runtime or install PostgreSQL."
    }
}
if (-not (Test-Path -LiteralPath (Join-Path $root '.venv\Scripts\python.exe'))) {
    throw 'Project virtual environment not found. Create it and install requirements.txt first.'
}
$env:PATH = "$pgBin;$env:PATH"

if (-not (Test-Path -LiteralPath $pgData)) {
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $bytes = New-Object byte[] 24
    $rng.GetBytes($bytes)
    $dbPassword = [BitConverter]::ToString($bytes).Replace('-', '').ToLowerInvariant()
    $rng.Dispose()

    $passwordFile = Join-Path $root '.pg_runtime\initdb-password.tmp'
    try {
        Set-Content -LiteralPath $passwordFile -Value $dbPassword -NoNewline -Encoding ascii
        & (Join-Path $pgBin 'initdb.exe') -D $pgData -U postgres --pwfile=$passwordFile --auth-local=trust --auth-host=scram-sha-256 --encoding=UTF8
        if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL cluster initialization failed.' }
    }
    finally {
        Remove-Item -LiteralPath $passwordFile -Force -ErrorAction SilentlyContinue
    }

    $databaseUrl = "postgresql+psycopg2://postgres:$dbPassword@127.0.0.1:5433/$dbName"
    Set-Content -LiteralPath $envFile -Value "CARDSENSE_DATABASE_URL=$databaseUrl" -Encoding ascii
}
elseif (Test-Path -LiteralPath $envFile) {
    $envLine = Get-Content -LiteralPath $envFile | Where-Object { $_ -match '^CARDSENSE_DATABASE_URL=' } | Select-Object -First 1
    if (-not $envLine) { throw '.env exists but CARDSENSE_DATABASE_URL is missing.' }
    $databaseUrl = $envLine.Substring('CARDSENSE_DATABASE_URL='.Length)
    if ($databaseUrl -notmatch '^postgresql\+psycopg2://postgres:([0-9a-f]+)@') {
        throw 'The CARDSENSE_DATABASE_URL in .env does not match the generated local PostgreSQL credential format.'
    }
    $dbPassword = $Matches[1]
}
else {
    throw 'Existing .pgdata found without .env credentials. Restore CARDSENSE_DATABASE_URL in .env or move the old local cluster aside before initializing a new one.'
}

$null = & (Join-Path $pgBin 'pg_ctl.exe') -D $pgData status 2>&1
if ($LASTEXITCODE -ne 0) {
    & (Join-Path $pgBin 'pg_ctl.exe') -D $pgData -l $pgLog -o '-h 127.0.0.1 -p 5433' -w start
    if ($LASTEXITCODE -ne 0) { throw "Could not start local PostgreSQL. Review $pgLog" }
}

$env:PGPASSWORD = $dbPassword
$env:CARDSENSE_DATABASE_URL = $databaseUrl
$dbExists = & (Join-Path $pgBin 'psql.exe') -h 127.0.0.1 -p 5433 -U postgres -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$dbName'"
if ($LASTEXITCODE -ne 0) { throw 'Could not connect to the local PostgreSQL server.' }
if ($dbExists.Trim() -ne '1') {
    & (Join-Path $pgBin 'createdb.exe') -h 127.0.0.1 -p 5433 -U postgres $dbName
    if ($LASTEXITCODE -ne 0) { throw "Could not create database $dbName." }
}

& (Join-Path $pgBin 'psql.exe') -h 127.0.0.1 -p 5433 -U postgres -d $dbName -v ON_ERROR_STOP=1 -f (Join-Path $root 'sql\01_create_schema.sql')
if ($LASTEXITCODE -ne 0) { throw 'Schema creation failed.' }

& (Join-Path $root '.venv\Scripts\python.exe') (Join-Path $root 'scripts\load_to_postgres.py')
if ($LASTEXITCODE -ne 0) { throw 'Loading the cleaned customer data failed.' }

& (Join-Path $pgBin 'psql.exe') -h 127.0.0.1 -p 5433 -U postgres -d $dbName -v ON_ERROR_STOP=1 -f (Join-Path $root 'sql\02_business_analysis.sql')
if ($LASTEXITCODE -ne 0) { throw 'Business analysis queries failed.' }

Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
Remove-Item Env:CARDSENSE_DATABASE_URL -ErrorAction SilentlyContinue
Write-Host "PostgreSQL phase complete. Database is local at 127.0.0.1:5433/$dbName. Credentials are stored in the Git-ignored .env file."
