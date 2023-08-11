from django.core.exceptions import PermissionDenied
from django.urls import reverse


class SitePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """ビューを呼び出す直前に実行される処理"""
        # 管理サイトのログイン画面はアクセス制限なし
        if request.path == '/admin/login/':
            return None

        # 権限を持っていないユーザーが「/admin/」配下にアクセスしたら 403エラー
        if request.path.startswith('/admin/'):
            if not (request.user.is_staff and request.user.is_active):
                raise PermissionDenied
