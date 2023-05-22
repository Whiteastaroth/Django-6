from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .filters import NewFilter

from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.views.decorators.csrf import csrf_protect
from .models import New, Subscription, Category


class NewsListView(ListView):
    model = New
    template_name = 'default.html'
    context_object_name = 'news'
    ordering = ['-data_pub']
    paginate_by = 10


class NewDetailView(DetailView):
    model = New
    template_name = 'detail.html'
    context_object_name = 'new'


class UncosNewsListView(ListView):
    model = New
    template_name = 'uncos.html'
    context_object_name = 'news'
    ordering = ['-data_pub']
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().filter(category='uncos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        current_page = context['page_obj']
        start_index = max(current_page.number - 2, 1)
        end_index = min(current_page.number + 2, paginator.num_pages)
        page_range = range(start_index, end_index + 1)
        context['page_range'] = page_range
        return context


class ArticlesNewsListView(ListView):
    model = New
    template_name = 'articles.html'
    context_object_name = 'news'
    ordering = ['-data_pub']
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().filter(category='articles')


class NewsSearchView(ListView):
    model = New
    template_name = 'news_search.html'
    context_object_name = 'news'
    ordering = ['-data_pub']
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return New.objects.filter(title__icontains=query)
        return New.objects.all()


def news_search(request):
    news_list = New.objects.all()
    news_filter = NewFilter(request.GET, queryset=news_list)
    return render(request, 'news_search.html', {'filter': news_filter, 'news_list': news_filter.qs})


class UncosCreateView(LoginRequiredMixin, CreateView):
    raise_exception = True
    permission_required = ('news.add_new',)
    model = New
    fields = ['title', 'text', 'category']
    template_name = 'news_form.html'


class UncosUpdateView(LoginRequiredMixin, UpdateView):
    permission_required = ('news.change_new',)
    model = New
    fields = ['title', 'text', 'category']
    template_name = 'news_edit.html'


class UncosDeleteView(LoginRequiredMixin, DeleteView):
    raise_exception = True
    permission_required = ('news.delete_new',)
    model = New
    success_url = reverse_lazy('index')
    template_name = 'news_confirm_delete.html'


class ArticlesCreateView(LoginRequiredMixin, CreateView):
    permission_required = ('news.add_new',)
    model = New
    fields = ['title', 'text', 'category']
    template_name = 'articles_form.html'


class ArticlesUpdateView(LoginRequiredMixin, UpdateView):
    permission_required = ('news.change_new',)
    model = New
    fields = ['title', 'text', 'category']
    template_name = 'articles_edit.html'


class ArticlesDeleteView(LoginRequiredMixin, DeleteView):
    permission_required = ('news.delete_new',)
    model = New
    success_url = reverse_lazy('articles')
    template_name = 'articles_confirm_delete.html'


@login_required
@csrf_protect
def subscriptions(request ):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = Category.objects.get(id=category_id)
        action = request.POST.get('action')

        if action == 'subscribe':
            Subscription.objects.create(user=request.user, category=category)
        elif action == 'unsubscribe':
            Subscription.objects.filter(
                user=request.user,
                category=category,
            ).delete()

    categories_with_subscriptions = Category.objects.annotate(
        user_subscribed=Exists(
            Subscription.objects.filter(
                user=request.user,
                category=OuterRef('pk'),
            )
        )
    ).order_by('name')
    return render(
        request,
        'news/registration/subscriptions.html',
        {'categories': categories_with_subscriptions},
    )

