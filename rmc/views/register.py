from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, HttpResponse
from django import forms

from rmc import models
from rmc.utils.bootstrap import BootStrapModelForm

from rmc.utils.encrypt import md5


########################################

class StudentRegistrationModelForm(BootStrapModelForm):
    email = forms.CharField(
        label="Email",
        widget=forms.EmailInput,
        required=True,
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(render_value=True),
        required=True,
    )
    confirm_password = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput,
        required=True,
    )

    class Meta:
        model = models.Student
        fields = ["email", "name", "password", "confirm_password", "gender", "age", "entry_date", "degree_programme"]
        widgets = {
            "password": forms.PasswordInput,
        }

    # Encrypts the password first
    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)

    # Then, verifies that the password entered twice is the same
    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm_pwd = md5(self.cleaned_data.get("confirm_password"))
        if confirm_pwd != pwd:
            raise ValidationError("Password and confirm password does not match.")

        return confirm_pwd


def student_registration(request):
    # (1) Calls the html page and passes the database data if a GET request is received
    if request.method == "GET":
        form = StudentRegistrationModelForm()
        return render(request, "registration.html", {"form": form})

    # (2) Gets the user input (a ModelForm instance) from the front-end POST request
    form = StudentRegistrationModelForm(data=request.POST)

    # (3) Validates the email
    if form.is_valid():
        # Verifies that the email exists
        obj_email = models.Student.objects.filter(email=form.cleaned_data.get("email")).first()

        if not obj_email:
            # Creates a new user
            # fields = ["email", "name", "password", "confirm_password", "gender", "age", "entry_date", "degree_programme"]
            models.Student.objects.create(email=form.cleaned_data.get("email"),
                                          name=form.cleaned_data.get("name"),
                                          password=form.cleaned_data.get("password"),
                                          gender=form.cleaned_data.get("gender"),
                                          age=form.cleaned_data.get("age"),
                                          entry_date=form.cleaned_data.get("entry_date"),
                                          degree_programme=form.cleaned_data.get("degree_programme"))

            return redirect("/login/")

        # Reports an error if the email exists
        else:
            form.add_error("email", "This email already exists.")

    return render(request, "registration.html", {"form": form})


class StaffRegistrationModelForm(BootStrapModelForm):
    email = forms.CharField(
        label="Email",
        widget=forms.EmailInput,
        required=True,
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(render_value=True),
        required=True,
    )
    confirm_password = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput,
        required=True,
    )

    class Meta:
        model = models.Staff
        fields = ["email", "name", "password", "confirm_password", "gender"]
        widgets = {
            "password": forms.PasswordInput,
        }

    # Encrypts the password first
    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)

    # Then, verifies that the password entered twice is the same
    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm_pwd = md5(self.cleaned_data.get("confirm_password"))
        if confirm_pwd != pwd:
            raise ValidationError("Password and confirm password does not match.")

        return confirm_pwd


def staff_registration(request):
    # (1) Calls the html page and passes the database data if a GET request is received
    if request.method == "GET":
        form = StaffRegistrationModelForm()
        return render(request, "staff-registration.html", {"form": form})

    # (2) Gets the user input (a ModelForm instance) from the front-end POST request
    form = StaffRegistrationModelForm(data=request.POST)

    # (3) Validates the email
    if form.is_valid():
        # Verifies that the email exists
        obj_email = models.Staff.objects.filter(email=form.cleaned_data.get("email")).first()

        if not obj_email:
            # Creates a new staff
            models.Staff.objects.create(email=form.cleaned_data.get("email"),
                                        name=form.cleaned_data.get("name"),
                                        password=form.cleaned_data.get("password"),
                                        gender=form.cleaned_data.get("gender"))

            return redirect("/staff-login/")

        # Reports an error if the email exists
        else:
            form.add_error("email", "This email already exists.")

    return render(request, "staff-registration.html", {"form": form})


########################################