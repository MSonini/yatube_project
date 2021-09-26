from django.http import HttpResponse

# Main page
def index(request):
    return HttpResponse('Main page')

# Groups page
def group_posts(request, slug):
    return HttpResponse(f'Group name: {slug}')
