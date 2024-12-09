from django.core.paginator import InvalidPage
from django.views.generic import ListView


class BaseListView(ListView):
    paginate_by = 20
    paginate_orphans = 3
    max_pages_display = 5

    def paginate_queryset(self, queryset, page_size):
        """
        Override to customize the pagination range logic.
        """
        paginator = self.get_paginator(queryset, page_size)
        page = self.request.GET.get('page', 1)

        try:
            page_number = int(page)
        except (ValueError, TypeError):
            page_number = 1

        try:
            page_obj = paginator.page(page_number)
        except InvalidPage:
            page_obj = paginator.page(1)

        # Custom page range logic
        max_pages_display = self.max_pages_display
        half_range = max_pages_display // 2
        current_page = page_obj.number

        if paginator.num_pages <= max_pages_display:
            custom_page_range = range(1, paginator.num_pages + 1)
        else:
            start_page = max(current_page - half_range, 1)
            end_page = min(current_page + half_range, paginator.num_pages)

            if current_page <= half_range:
                end_page = min(max_pages_display, paginator.num_pages)
            elif current_page + half_range > paginator.num_pages:
                start_page = paginator.num_pages - max_pages_display + 1

            custom_page_range = range(start_page, end_page + 1)

        # Add custom page range to context
        self.extra_context = self.extra_context or {}
        self.extra_context['custom_page_range'] = custom_page_range

        return paginator, page_obj, page_obj.object_list, page_obj.has_other_pages()
