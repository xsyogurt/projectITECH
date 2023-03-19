from django.contrib import admin
from rmc.models import Student, Course, CourseReview, DegreeProgramme, Staff


admin.site.register(Student)
admin.site.register(Course)
admin.site.register(CourseReview)
admin.site.register(DegreeProgramme)
admin.site.register(Staff)

