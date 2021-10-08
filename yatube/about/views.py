from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Об Авторе'
        context['text'] = ('На создание этой страницы '
                           'у меня ушло пять минут! Ай да я.')
        context['header'] = 'Привет, я автор'
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Об Авторе'
        context['text'] = ('На создание этой страницы '
                           'у меня ушло пять минут! Ай да я.')

        return context
