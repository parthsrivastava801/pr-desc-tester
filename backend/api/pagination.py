import math

def paginate_queryset(queryset, page, page_size):
    """
    Paginates a queryset.
    """
    total_count = len(queryset)
    # Fixed the off-by-one bug here: total_pages = math.ceil(total_count / page_size) + 1 was wrong
    total_pages = math.ceil(total_count / page_size) if page_size > 0 else 0
    
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        'total_count': total_count,
        'total_pages': total_pages,
        'current_page': page,
        'results': queryset[start:end]
    }
