from django.shortcuts import render

def my_view(request):
    context = {'message': 'Bonjour, caca!'}
    return render(request, 'my_template.html', context)
