from django.urls import path
from . import views

urlpatterns = [
    path("courses/", views.course_list, name="course_list"),

    # static paths 
    path("courses/add/", views.course_create, name="course_add"),

    # enrol/unenrol, materials, feedback, teacher actions...
    path("courses/<slug:slug>/enroll/", views.enroll, name="course_enroll"),
    path("courses/<slug:slug>/enrol/",  views.enroll, name="course_enrol_alias"),
    path("courses/<slug:slug>/unenroll/", views.unenroll, name="course_unenroll"),
    path("courses/<slug:slug>/unenrol/",  views.unenroll, name="course_unenrol_alias"),
    path("courses/<slug:slug>/materials/add/", views.material_add, name="material_add"),
    path("courses/<slug:slug>/feedback/", views.feedback_submit, name="feedback_submit"),
    path("courses/<slug:slug>/unenrol/<str:username>/", views.teacher_remove_student, name="teacher_remove_student"),
    path("courses/<slug:slug>/block/<str:username>/",   views.teacher_block_student,   name="teacher_block_student"),
    path("courses/<slug:slug>/unblock/<str:username>/", views.teacher_unblock_student, name="teacher_unblock_student"),

    # keep this AFTER all specific routes
    path("courses/<slug:slug>/", views.course_detail, name="course_detail"),
]
