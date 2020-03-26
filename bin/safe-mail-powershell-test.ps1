$inFile = './tests/files/'
$inFileName = 'Phish Test - 1.eml'
$outFile = 'output.zip'
$URL = 'http://localhost:7001/email'

$fileBytes = [System.IO.File]::ReadAllBytes($inFile + $inFileName);
$fileEnc = [System.Text.Encoding]::GetEncoding('UTF-8').GetString($fileBytes);
$boundary = [System.Guid]::NewGuid().ToString(); 
$LF = "`r`n";

$bodyLines = ( 
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"$($inFileName)`"",
    "Content-Type: application/octet-stream$LF",
    $fileEnc,
    "--$boundary--$LF" 
) -join $LF

Invoke-RestMethod -Uri $URL -Method Post -ContentType "multipart/form-data; boundary=`"$boundary`"" -Body $bodyLines -OutFile $outFile