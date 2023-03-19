from django.shortcuts import render, redirect, HttpResponse
from django import forms

from rmc import models
from rmc.utils.bootstrap import BootStrapModelForm

from rmc.utils.encrypt import md5
from rmc.utils.captcha import check_code
from io import BytesIO


########################################

# Verification code image
def captcha(request):
    img, code_string = check_code()

    # Digit code for authentication, code_string
    # print(code_string)

    # Writes the image verification code to the session
    request.session["captcha"] = code_string
    # Sets the expiry time (60s) for the image verification code
    request.session.set_expiry(60)

    stream = BytesIO()
    img.save(stream, "png")
    return HttpResponse(stream.getvalue())


########################################

# Student login
class StudentLoginModelForm(BootStrapModelForm):
    # Email and password must not be empty
    email = forms.CharField(
        label="Email",
        required=True,
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        required=True,
    )

    # Verification code
    verification_code = forms.CharField(
        label="Verification code",
        widget=forms.TextInput,
        required=True,
    )

    class Meta:
        model = models.Student
        fields = ["email", "password"]

    # For password authentication
    # Encrypts user input using md5
    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)


def student_login(request):
    if request.method == "GET":
        form = StudentLoginModelForm()
        return render(request, "login.html", {"form": form})

    form = StudentLoginModelForm(data=request.POST)
    if form.is_valid():

        # CAPTCHA test, before user authentication
        vcode_user_input = form.cleaned_data.pop("verification_code")
        vcode = request.session.get("captcha", "")
        if vcode.upper() != vcode_user_input.upper():
            form.add_error("verification_code", "Wrong verification code")
            return render(request, "login.html", {"form": form})

        # User authentication
        # (1) Retrieves existing student objects from the database
        student_object = models.Student.objects.filter(**form.cleaned_data).first()

        # (2) If authentication fails
        if not student_object:
            # Reports the error
            form.add_error("password", "Incorrect email or password")
            return render(request, "login.html", {"form": form})

        # (3) If authentication passes
        #     Creates a session for the user
        request.session["info"] = {"id": student_object.id, "email": student_object.email, "name": student_object.name}

        # Resets the expiry time (1 day) for re-login
        request.session.set_expiry(60 * 60 * 24)

        return redirect("/student-info/")

    return render(request, "login.html", {"form": form})


########################################

# Staff login
class StaffLoginModelForm(BootStrapModelForm):
    # Email and password must not be empty
    email = forms.CharField(
        label="Email",
        required=True,
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        required=True,
    )

    # Verification code
    verification_code = forms.CharField(
        label="Verification code",
        widget=forms.TextInput,
        required=True,
    )

    class Meta:
        model = models.Staff
        fields = ["email", "password"]

    # For password authentication
    # Encrypts user input using md5
    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)


def staff_login(request):
    if request.method == "GET":
        form = StaffLoginModelForm()
        return render(request, "staff-login.html", {"form": form})

    form = StaffLoginModelForm(data=request.POST)
    if form.is_valid():

        # CAPTCHA test, before user authentication
        vcode_user_input = form.cleaned_data.pop("verification_code")
        vcode = request.session.get("captcha", "")
        if vcode.upper() != vcode_user_input.upper():
            form.add_error("verification_code", "Wrong verification code")
            return render(request, "staff-login.html", {"form": form})

        # User authentication
        # (1) Retrieves existing student objects from the database
        staff_object = models.Staff.objects.filter(**form.cleaned_data).first()

        # (2) If authentication fails
        if not staff_object:
            # Reports the error
            form.add_error("password", "Incorrect email or password")
            return render(request, "staff-login.html", {"form": form})

        # (3) If authentication passes
        #     Creates a session for the user
        request.session["info"] = {"id": staff_object.id, "email": staff_object.email, "name": staff_object.name}

        # Resets the expiry time (1 day) for re-login
        request.session.set_expiry(60 * 60 * 24)

        return redirect("/data-visualisation/")

    return render(request, "staff-login.html", {"form": form})


########################################

# Student logout
def logout(request):
    request.session.clear()
    return redirect("/login/")


########################################

# Staff logout
def staff_logout(request):
    request.session.clear()
    return redirect("/staff-login/")


########################################



