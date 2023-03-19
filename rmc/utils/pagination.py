"""
Instructions for use


[1] views.py
def func(request):

    # (1) Retrieves data from the database
    queryset = models.xxxx.objects.all()

    # (2) Initialises a pagination object
    pagination_object = Pagination(request, queryset)

    contents = {
        # Organises the retrieved data with pagination
        "queryset": pagination_object.queryset_page,

        # Generates front-end code for pagination
        "tpl_pagination_navbar": pagination_object.tpl(),
    }

    return render(request, "xxxx.html", contents)


[2] xxxx.html
<body>
    ...
    {% for obj in queryset %}
        {{ obj.xx }}
    {% endfor %}
    ...
    <!-- Pagination -->
    <div class="clearfix">
        <ul class="pagination">
            {{ tpl_pagination_navbar }}
        </ul>
    </div>
    ...
</body>


"""

from django.utils.safestring import mark_safe
import copy


class Pagination(object):

    def __init__(self, request, queryset, page_size=10, page_param="page", deviation=5):

        query_dict = copy.deepcopy(request.GET)
        query_dict._mutable = True
        self.query_dict = query_dict
        self.page_param = page_param

        # (1) Gets the current page number
        page = request.GET.get(page_param, "1")
        if page.isdecimal():
            page = int(page)
        else:
            page = 1
        self.page = page

        # (2) Sets the pagination block size
        #     For example, 10 data entries per page
        self.page_size = page_size
        self.data_start = (page - 1) * page_size
        self.data_end = page * page_size

        # (3) Slices data by the pagination block size
        self.queryset_page = queryset[self.data_start:self.data_end]

        # (4) Counts the number of all data entries
        data_count = queryset.count()

        # (5) Calculates the total number of pages
        page_count, remainder = divmod(data_count, page_size)
        if remainder:
            page_count += 1
        self.page_count = page_count

        # (6) Sets (the current page ±5) buttons for user navigation
        #     Displays page buttons ranging from [current page -5, current page +5]
        self.deviation = deviation

        # (7) Bug fix for page redirection
        if self.page <= self.page_count:
            self.queryset_page = queryset[self.data_start:self.data_end]
        else:
            self.page = 1
            self.queryset_page = queryset[0:self.page_size]


    def tpl(self):

        # (7) Sets rules for the range of page numbers displayed in the pagination navbar
        # The number of pages is less than 11 (2*5+1)
        if self.page_count <= 2 * self.deviation + 1:
            page_start = 1
            page_end = self.page_count

        # The number of pages is greater than 11 (2*5+1)
        else:
            # The current page is less than 5
            if self.page <= self.deviation:
                page_start = 1
                page_end = 2 * self.deviation + 1
            else:
                # The current page is greater than 5
                # The current page + 5 is greater than the total number of pages
                if (self.page + self.deviation) > self.page_count:
                    page_start = self.page_count - 2 * self.deviation
                    page_end = self.page_count
                else:
                    page_start = self.page - self.deviation
                    page_end = self.page + self.deviation

        # (8) Generates front-end code for pagination
        pagination_code = []

        # The first page
        self.query_dict.setlist(self.page_param, [1])
        pagination_code.append('<li><a href="?{}">First</a></li>'.format(self.query_dict.urlencode()))

        # Previous page
        if self.page > 1:
            self.query_dict.setlist(self.page_param, [self.page - 1])
            tpl_prev = '<li><a href="?{}">< Priv</a></li>'.format(self.query_dict.urlencode())
        else:
            self.query_dict.setlist(self.page_param, [1])
            tpl_prev = '<li><a href="?{}">< Priv</a></li>'.format(self.query_dict.urlencode())
        pagination_code.append(tpl_prev)

        # Displays the 5 pages before and after the current page
        for i in range(page_start, page_end + 1):
            self.query_dict.setlist(self.page_param, [i])
            if i == self.page:
                tpl = '<li class="active"><a href="?{}">{}</a></li>'.format(self.query_dict.urlencode(), i)
            else:
                tpl = '<li><a href="?{}">{}</a></li>'.format(self.query_dict.urlencode(), i)
            pagination_code.append(tpl)

        # Next page
        if self.page < self.page_count:
            self.query_dict.setlist(self.page_param, [self.page + 1])
            tpl_next = '<li><a href="?{}">Next ></a></li>'.format(self.query_dict.urlencode())
        else:
            self.query_dict.setlist(self.page_param, [self.page_count])
            tpl_next = '<li><a href="?{}">Next ></a></li>'.format(self.query_dict.urlencode())
        pagination_code.append(tpl_next)

        # The last page
        self.query_dict.setlist(self.page_param, [self.page_count])
        pagination_code.append('<li><a href="?{}">Last</a></li>'.format(self.query_dict.urlencode()))


        tpl_redirect = """
        <li>
            <form method="get" style="float: left; margin-left: -1px;">
                <input class="form-control" name="page" type="text" placeholder="Page number"
                       style="display: inline-block; float: left; width: 110px; position: relative; border-radius: 0;">
                <button class="btn btn-default" type="submit" style="border-radius: 0">Redirect</button>
            </form>
        </li>
        """
        pagination_code.append(tpl_redirect)

        # Encapsulates the pagination code
        pagination = mark_safe("".join(pagination_code))

        return pagination
