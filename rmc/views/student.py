from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from django import forms
from django.views.decorators.csrf import csrf_exempt

from rmc import models
from rmc.utils.bootstrap import BootStrapModelForm
from rmc.utils.pagination import Pagination
from rmc.utils.encrypt import md5


def student_info(request):
    info = request.session["info"]

    # Get the data in rmc_student based on the login ID
    student = models.Student.objects.get(email=info['email'])
    stu_info = {
        "email": student.email,
        "name": student.name,
        "gender": student.get_gender_display(),
        "age": student.age,
        "entry_date": student.entry_date.strftime("%Y-%m-%d"),
        "degree_programme": student.degree_programme.name,
    }
    return render(request, "student-info.html", {"stu_info": stu_info})


class StudentInfoModelForm(BootStrapModelForm):
    class Meta:
        model = models.Student
        fields = ['name', 'gender', 'age']


def student_edit(request):
    """ Edit Student Profile """
    info = request.session["info"]
    student = models.Student.objects.filter(id=info['id']).first()

    if request.method == "GET":
        # Retrieve the row of data to be edited from the database based on the ID
        form = StudentInfoModelForm(instance=student)

        return render(request, 'student-edit.html', {"form": form})

    # Get the user input (a ModelForm instance) from the front-end POST request
    form = StudentInfoModelForm(data=request.POST, instance=student)
    if form.is_valid():
        form.save()
        return redirect('/student-info/')
    return render(request, 'student-edit.html', {"form": form})


class AddCommentModelForm(BootStrapModelForm):
    # Restrict the score input range to 1-10
    overall_score = forms.IntegerField(
        label="Overall Score",
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    easiness_score = forms.IntegerField(
        label="Easiness Score",
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    interest_score = forms.IntegerField(
        label="Interest Score",
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    usefulness_score = forms.IntegerField(
        label="Usefulness Score",
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    teaching_score = forms.IntegerField(
        label="Teaching Score",
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )

    class Meta:
        model = models.CourseReview
        exclude = ['student_id', 'course_id']
        # Set the comment field to a 10 row text area
        widgets = {
            'comment': forms.Textarea(attrs={
                "rows": 10,
            })
        }


def student_course(request):
    """ Student Course """
    stu_id = request.session["info"]['id']
    stu_prog = models.Student.objects.get(id=stu_id).degree_programme.name

    # Get all courses by name of degree_programme
    degree_id = models.DegreeProgramme.objects.get(name=stu_prog).id
    queryset = models.Course.objects.filter(associated_degree_programmes=degree_id)
    for i in queryset:
        i.isComment = 0
        isComment = models.CourseReview.objects.filter(student_id=stu_id, course_id=i.id).first()
        if isComment is not None:
            i.isComment = 1

    pagination_object = Pagination(request, queryset)

    course = AddCommentModelForm()
    contents = {
        "queryset": pagination_object.queryset_page,
        "tpl_pagination_navbar": pagination_object.tpl(),
        "course": course,
    }

    return render(request, 'student-course.html', contents)


@csrf_exempt
def student_addcomment(request):
    """ Student Add Comment """
    # Get the student ID and course ID from the front-end request
    stu_id = request.session["info"]['id']
    uid = request.GET.get("uid")

    # Check if the student has already commented on the course
    row_object = models.CourseReview.objects.filter(student_id=stu_id, course_id=uid).first()
    if row_object is not None:
        return JsonResponse({"status": False, 'tips': "You have already commented"})
    form = AddCommentModelForm(data=request.POST)

    if form.is_valid():
        # Get the student and course object from database based on the ID
        stu_obj = models.Student.objects.filter(id=stu_id).first()
        uid_obj = models.Course.objects.filter(id=uid).first()
        form.instance.student_id = stu_obj
        form.instance.course_id = uid_obj
        form.save()
        return JsonResponse({"status": True})

    return JsonResponse({"status": False, 'error': form.errors})


def student_comment(request):
    """ Show Student Comment """
    # Retrieve the comment data from the database based on the student ID
    stu_id = request.session["info"]['id']
    queryset = models.CourseReview.objects.filter(student_id=stu_id)
    pagination_object = Pagination(request, queryset)
    contents = {
        "queryset": pagination_object.queryset_page,
        "tpl_pagination_navbar": pagination_object.tpl(),
    }
    return render(request, 'student-comment.html', contents)


class StudentResetModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = models.Staff
        fields = ["password", "confirm_password"]
        widgets = {
            "password": forms.PasswordInput,
            "required": True,
        }

    # Encrypts the password first
    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        md5_pwd = md5(pwd)

        # Compares the user input with the existing password
        # and report an error if it matches, otherwise save the user input as the new password
        exists = models.Student.objects.filter(id=self.instance.pk, password=md5_pwd).exists()
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


def student_reset(request, studentid):
    # Verifies that the id in the url path is valid
    row_object = models.Student.objects.filter(id=studentid).first()
    if not row_object:
        return redirect("/student-info/")

    title = "Reset password for {}".format(row_object.name)

    # Returns input boxes according to the database table structure
    if request.method == "GET":
        form = StudentResetModelForm()
        return render(request, "reset-password.html", {"form": form, "title": title})

    # Verifies the user input and saves
    form = StudentResetModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect("/student-info")

    return render(request, "reset-password.html", {"form": form, "title": title})








