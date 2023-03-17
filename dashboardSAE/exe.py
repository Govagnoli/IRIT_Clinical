from django.shortcuts import render
import subprocess

def execute_exe(request):
    if request.method == 'POST':
        subprocess.run(".\\dist\\majBD.exe", shell=True)
    return render(request, 'execute_exe.html')
