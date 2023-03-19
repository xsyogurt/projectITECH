from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect

class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):

        # (1) If requesting the login page, continue
        #     Gets the URL of the user request, request.path_info
        # if request.path_info == "/login/":
        if request.path_info in ["/login/", "/staff-login/", "/admin/", "/registration/", "/staff-registration/", "/captcha/",]:
            return

        # (2) If the session info can be found in the database,
        #     it means that the user has completed the login, continue
        info_dict = request.session.get("info")
        if info_dict:
            return

        # (3) Redirects to the login page for those has not completed the login
        return redirect("/login/")
