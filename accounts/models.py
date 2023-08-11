from django.contrib.auth.models import AbstractUser
# from django.contrib.auth.signals import user_logged_in
from django.db import models


class CustomUser(AbstractUser):
    """拡張ユーザーモデル"""

    class Meta(object):
        db_table = 'custom_user'
        verbose_name = verbose_name_plural = 'カスタムユーザー'

    login_count = models.IntegerField(verbose_name='ログイン回数', default=0)
    profile_image = models.ImageField(verbose_name='プロフィール画像',
                                      null=True, blank=True)

    def post_login(self):
        """ログイン後処理"""
        # ログイン回数を増やす
        self.login_count += 1
        self.save()

# def update_login_count(sender, user, **kwargs):
#     """
#     A signal receiver which updates the last_login date for
#     the user logging in.
#     """
#     user.login_count += 1
#     user.save(update_fields=['login_count'])
#
#
# user_logged_in.connect(update_login_count)
