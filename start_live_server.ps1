# Deschide VS Code și pornește Live Server automat pe index.html
code ./frontend/index.html

Start-Sleep -Seconds 2

# Trimite comanda către VS Code ca să pornească Live Server
$wshell = New-Object -ComObject wscript.shell;
$wshell.AppActivate('Visual Studio Code');
Start-Sleep -Milliseconds 700
$wshell.SendKeys("^F5")
