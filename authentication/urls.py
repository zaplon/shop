from django.conf.urls import url

from authentication import views

urlpatterns = [
    #url(r'^register/$', views.register, name='register'),
    # url(r'^register/$', views.RegistrationView.as_view(), name='register'),
    # url(r'^register/verify/$', 'password_reset', {
    #     'template_name': 'registration/initial_password.html',
    #     'email_template_name': 'registration/verification.html',
    #     'subject_template_name': 'registration/vericiation_subject.txt',
    #     'post_reset_redirect': 'authentication:register-done',
    # }, name='register-password'),
    # url(r'^register/done/$', 'password_reset_done', {
    #     'template_name': 'registration/initial_done.html',
    # }, name='register-done'),
    #
    # url(r'^register/password/$', 'password_reset', {
    #     'template_name': 'registration/initial_confirm.html',
    #     'post_reset_redirect': 'authentication:register-complete',
    # }, name='register-confirm'),
    # url(r'^register/complete/$', 'password_reset_complete', {
    #     'template_name': 'registration/initial_complete.html',
    # }, name='register-complete'),

    url(r'^password-reset/$', views.password_reset, name='password_reset'),
    url(r'^password-reset-done/$', views.password_reset_done, name='password_reset_done'),

]