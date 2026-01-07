from django.shortcuts import render

def hand_scan_view(request):
    # This just tells Django which HTML file to show
    return render(request, 'tracker.html')
def home(request):
    return render(request, 'home.html')