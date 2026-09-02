' Dictado EN/ES con Whisper - arranque silencioso en segundo plano (sin ventana)
' F8 = escribir en español  |  F9 = escribir en inglés  (funciona en cualquier app)
Set WshShell = CreateObject("WScript.Shell")
Set env = WshShell.Environment("PROCESS")
env("PYTHONPATH") = "D:\Hermes\dictation\src"
WshShell.Run """D:\Hermes\dictation\.venv\Scripts\python.exe"" -m vozlocal", 0, False
