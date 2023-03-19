from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, HttpResponse
from django import forms

from rmc import models
from rmc.utils.bootstrap import BootStrapModelForm
from rmc.utils.pagination import Pagination
from rmc.utils.encrypt import md5

from pyecharts import options as opts
from pyecharts.charts import Page, Grid, Bar, Pie
from pyecharts.globals import ThemeType


########################################

def course_management(request):
    # Gets all the data in the rmc_course
    # associated_degree_programmes = models.ManyToManyField(to="DegreeProgramme", related_name="degree_programme_courses")
    courses = models.Course.objects.prefetch_related("associated_degree_programmes").all()

    pagination_object = Pagination(request, courses)

    contents = {
        # Organises the retrieved data with pagination
        "queryset": pagination_object.queryset_page,

        # Generates front-end code for pagination
        "tpl_pagination_navbar": pagination_object.tpl(),
    }

    # Sends the queryset to the front-end
    return render(request, "course-management.html", contents)


class CourseModelForm(BootStrapModelForm):
    class Meta:
        model = models.Course
        fields = ["name", "associated_degree_programmes"]


def course_add(request):
    # (1) Calls the html page and passes the database data if a GET request is received
    if request.method == "GET":
        # (1.1) Instantiates a ModelForm object
        form = CourseModelForm()

        # (1.2) Sends the ModelForm instance to the front-end
        return render(request, "course-add.html", {"form": form})

    # (2) Gets the user input (a ModelForm instance) from the front-end POST request
    form = CourseModelForm(data=request.POST)

    # (3) Validates the user input
    if form.is_valid():
        # print(form.cleaned_data)

        # Saves the user input into the database
        form.save()
        return redirect("/course-management/")
    else:
        # print(form.errors)

        # Sends the error messages to the front-end
        return render(request, "course-add.html", {"form": form})


def course_edit(request, courseid):
    # (1) Receives the course ID via URL
    # http://127.0.0.1:8000/1/course-edit/

    # (2.1) Gets the existing data from the database according to the course ID
    row_object = models.Course.objects.filter(id=courseid).first()

    # (2) Calls the html page and passes the database data if a GET request is received
    if request.method == "GET":
        # (2.1) Gets the existing data from the database according to the course ID
        # row_object = models.Course.objects.filter(id=courseid).first()

        # (2.2) Instantiates a ModelForm object and passes the existing database data
        form = CourseModelForm(instance=row_object)

        # (2.3) Sends the ModelForm instance to the front-end
        return render(request, "course-edit.html", {"form": form})

    # (3) Gets the user input (a ModelForm instance) from the front-end POST request,
    # and updates the existing database data
    # row_object = models.Course.objects.filter(id=courseid).first()
    form = CourseModelForm(data=request.POST, instance=row_object)

    # (4) Validates the user input
    if form.is_valid():
        # Saves the user input into the database
        form.save()
        return redirect("/course-management/")

    # (5) Sends the error messages to the front-end
    return render(request, "course-edit.html", {"form": form})


def course_delete(request, courseid):
    models.Course.objects.filter(id=courseid).delete()
    return redirect("/course-management/")


########################################

def student_list(request):
    # Gets all the data in the rmc_student
    students = models.Student.objects.all()

    # Gets all the students who have made the course reviews
    students_review = models.CourseReview.objects.all().values("student_id").distinct()
    # students_review = models.CourseReview.objects.all().values("student_id",
    #                                                     "student_id__email",
    #                                                     "student_id__name",
    #                                                     "student_id__gender",
    #                                                     "student_id__age",
    #                                                     "student_id__entry_date",
    #                                                     "student_id__degree_programme__name")

    pagination_object = Pagination(request, students)

    contents = {
        "students_review": students_review,

        # Organises the retrieved data with pagination
        "queryset": pagination_object.queryset_page,

        # Generates front-end code for pagination
        "tpl_pagination_navbar": pagination_object.tpl(),
    }

    # Sends the queryset to the front-end
    return render(request, "student-list.html", contents)


def view_reviews_student(request, studentid):
    # (1) Receives the student ID via URL
    # http://127.0.0.1:8000/1/view-reviews-student/

    # (2) Gets the existing data from the database according to the student ID
    reviews = models.CourseReview.objects.filter(student_id=studentid)

    # (3) Extracts the student name from the queryset for display
    for row in reviews:
        student_name = row.student_id.name

    pagination_object = Pagination(request, reviews)

    contents = {
        "student_name": student_name,

        # Organises the retrieved data with pagination
        "queryset": pagination_object.queryset_page,

        # Generates front-end code for pagination
        "tpl_pagination_navbar": pagination_object.tpl(),
    }

    # (4) Sends the queryset to the front-end
    return render(request, "view-reviews-student.html", contents)


########################################

def course_list(request):
    # Gets all the data in the rmc_course
    courses = models.Course.objects.all()

    # Gets all the courses who have the course reviews
    courses_review = models.CourseReview.objects.all().values("course_id").distinct()

    pagination_object = Pagination(request, courses)

    contents = {
        "courses_review": courses_review,

        # Organises the retrieved data with pagination
        "queryset": pagination_object.queryset_page,

        # Generates front-end code for pagination
        "tpl_pagination_navbar": pagination_object.tpl(),
    }

    # Sends the queryset to the front-end
    return render(request, "course-list.html", contents)


def view_reviews_course(request, courseid):
    # (1) Receives the student ID via URL
    # http://127.0.0.1:8000/1/view-reviews-course/

    # (2) Gets the existing data from the database according to the student ID
    reviews = models.CourseReview.objects.filter(course_id=courseid)

    # (3) Extracts the course name from the queryset for display
    for row in reviews:
        course_name = row.course_id.name

    pagination_object = Pagination(request, reviews)

    contents = {
        "course_name": course_name,

        # Organises the retrieved data with pagination
        "queryset": pagination_object.queryset_page,

        # Generates front-end code for pagination
        "tpl_pagination_navbar": pagination_object.tpl(),
    }

    # (4) Sends the queryset to the front-end
    return render(request, "view-reviews-course.html", contents)


########################################

# Reset password
class StaffResetModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = models.Staff
        fields = ["password", "confirm_password"]
        widgets = {
            "password": forms.PasswordInput,
        }

    # Encrypts the password first
    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        md5_pwd = md5(pwd)

        # Compares the user input with the existing password
        # and report an error if it matches, otherwise save the user input as the new password
        exists = models.Staff.objects.filter(id=self.instance.pk, password=md5_pwd).exists()
        if exists:
            raise ValidationError("The new password should not be the same as the old one.")

        return md5_pwd

    # Then, verifies that the password entered twice is the same
    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm_pwd = md5(self.cleaned_data.get("confirm_password"))
        if confirm_pwd != pwd:
            raise ValidationError("The confirm password does not match the password.")

        return confirm_pwd


def staff_reset(request, staffid):
    # Verifies that the id in the url path is valid
    row_object = models.Staff.objects.filter(id=staffid).first()
    if not row_object:
        return redirect("/course-management")

    title = "Reset password for {}".format(row_object.name)

    # Returns input boxes according to the database table structure
    if request.method == "GET":
        form = StaffResetModelForm()
        return render(request, "reset-password.html", {"form": form, "title": title})

    # Verifies the user input and saves
    form = StaffResetModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect("/course-management/")

    return render(request, "reset-password.html", {"form": form, "title": title})


########################################

# Data visualisation
def data_visualisation(request):
    return render(request, "data-visualisation.html")


def gender_distribution_socs(request):
    page = Page(layout=Page.SimplePageLayout)

    student_male_count = models.Student.objects.filter(gender=1).count()
    student_female_count = models.Student.objects.filter(gender=2).count()

    # Creates a grid layout
    grid = Grid(init_opts=opts.InitOpts(theme=ThemeType.INFOGRAPHIC))

    # Creates a pie chart
    pie = Pie()
    pie.set_global_opts(title_opts=opts.TitleOpts(title="Gender Distribution in SoCS", subtitle=""))

    pie.add("", list(zip(["Male", "Female"], [student_male_count, student_female_count])))
    pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}:{c}\n{d}%)"))

    grid.add(pie, grid_opts=opts.GridOpts(pos_right="0%"))
    page.add(grid)
    return HttpResponse(page.render_embed())


def degree_programme_enrolment(request):
    page = Page(layout=Page.SimplePageLayout)

    degree_programmes = models.DegreeProgramme.objects.all()

    degree_programme_names = []
    for i in degree_programmes:
        degree_programme_names.append(i.name)

    student_cs_count = models.Student.objects.filter(degree_programme="Computing Science MSc").count()
    student_ds_count = models.Student.objects.filter(degree_programme="Data Science MSc").count()
    student_it_count = models.Student.objects.filter(degree_programme="Information Technology MSc").count()
    student_sd_count = models.Student.objects.filter(degree_programme="Software Development MSc").count()

    student_count_list = [student_cs_count, student_ds_count, student_it_count, student_sd_count]

    # Creates a grid layout
    grid = Grid(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS, ))

    # Creates a bar chart
    bar = Bar()

    bar.add_xaxis(degree_programme_names)
    bar.add_yaxis("Number of Students Enrolled", student_count_list)
    bar.set_global_opts(xaxis_opts=opts.AxisOpts(name_rotate=60, axislabel_opts={"rotate": 15}))

    grid.add(bar, grid_opts=opts.GridOpts(pos_right="0%"))
    page.add(grid)
    return HttpResponse(page.render_embed())


########################################

# def staff_info(request, staffid):
#     queryset = models.Staff.objects.filter(id=staffid).first()
#
#     return render(request, "staff-info.html", queryset)


########################################