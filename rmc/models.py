from django.db import models


# (1) Table rmc_student
class Student(models.Model):
    email = models.CharField(verbose_name="Email", max_length=64, null=True, blank=True)
    name = models.CharField(verbose_name="Name", max_length=32)
    password = models.CharField(verbose_name="Password", max_length=64)

    gender_choices = (
        (1, "Male"),
        (2, "Female"),
    )
    gender = models.SmallIntegerField(verbose_name="Gender", choices=gender_choices)

    age = models.IntegerField(verbose_name="Age")
    entry_date = models.DateField(verbose_name="Date of entry")

    degree_programme = models.ForeignKey(to="DegreeProgramme", to_field="name", on_delete=models.CASCADE)


# (2) Table rmc_course
class Course(models.Model):
    name = models.CharField(verbose_name="Name", max_length=64)
    associated_degree_programmes = models.ManyToManyField(to="DegreeProgramme", related_name="degree_programme_courses")


# (3) Table rmc_coursereview
class CourseReview(models.Model):
    student_id = models.ForeignKey(to="Student", to_field="id", on_delete=models.CASCADE)
    course_id = models.ForeignKey(to="Course", to_field="id", on_delete=models.CASCADE)

    overall_score = models.IntegerField(verbose_name="Overall score")
    easiness_score = models.IntegerField(verbose_name="Easiness score")
    interest_score = models.IntegerField(verbose_name="Interest score")
    usefulness_score = models.IntegerField(verbose_name="Usefulness score")
    teaching_score = models.IntegerField(verbose_name="Teaching score")

    comment = models.CharField(max_length=300, default='')


# (4) Table rmc_degreeprogramme
class DegreeProgramme(models.Model):
    name = models.CharField(verbose_name="Degree programme name", max_length=32, unique=True)
    level_choices = (
        (1, "Undergraduate"),
        (2, "Postgraduate"),
    )
    level = models.SmallIntegerField(verbose_name="Level", choices=level_choices)

    # programme_courses = models.ManyToManyField(to="Course", related_name="programme_courses")

    # The following code is used to improve the ModelForm implementation
    # so that the degree names are displayed on the front-end instead of the object names
    def __str__(self):
        return self.name


# (5) Table rmc_staff
class Staff(models.Model):
    email = models.CharField(verbose_name="Email", max_length=64, null=True, blank=True)
    name = models.CharField(verbose_name="Name", max_length=32)
    password = models.CharField(verbose_name="Password", max_length=64)

    gender_choices = (
        (1, "Male"),
        (2, "Female"),
    )
    gender = models.SmallIntegerField(verbose_name="Gender", choices=gender_choices)

