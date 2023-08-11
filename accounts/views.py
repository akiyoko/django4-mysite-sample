import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login as auth_login, logout as auth_logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
# from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import UpdateView

from .forms import LoginForm, ProfileChangeForm, RegisterForm

User = get_user_model()
logger = logging.getLogger(__name__)


class RegisterView(View):
    def get(self, request, *args, **kwargs):
        # すでにログインしている場合はショップ画面へリダイレクト
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('shop:index'))

        context = {
            'form': RegisterForm(),
        }
        return TemplateResponse(request, 'accounts/register.html', context)

    def post(self, request, *args, **kwargs):
        logger.info("You're in post!!!")

        # リクエストからフォームを作成
        form = RegisterForm(request.POST)
        # バリデーション
        if not form.is_valid():
            # バリデーションNGの場合はアカウント登録画面のテンプレートを再表示
            return TemplateResponse(request, 'accounts/register.html', {'form': form})

        # 保存する前に一旦取り出す
        user = form.save(commit=False)
        # パスワードをハッシュ化してセット
        user.set_password(form.cleaned_data['password'])
        # ユーザーオブジェクトを保存
        user.save()

        # ログイン処理（取得した Userオブジェクトをセッションに保存 & Userデータを更新）
        auth_login(request, user)

        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)


register = RegisterView.as_view()


class LoginView(View):
    def get(self, request, *args, **kwargs):
        """GETリクエスト用のメソッド"""
        # すでにログインしている場合はショップ画面へリダイレクト
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('shop:index'))

        context = {
            'form': LoginForm(),
        }
        # ログイン画面用のテンプレートに値が空のフォームをレンダリング
        return TemplateResponse(request, 'accounts/login.html', context)

    def post(self, request, *args, **kwargs):
        """POSTリクエスト用のメソッド"""
        # リクエストからフォームを作成
        form = LoginForm(request.POST)
        # バリデーション（ユーザーの認証も合わせて実施）
        if not form.is_valid():
            # バリデーションNGの場合はログイン画面のテンプレートを再表示
            return TemplateResponse(request, 'accounts/login.html', {'form': form})

        # ユーザーオブジェクトをフォームから取得
        user = form.get_user()

        # ログイン処理（取得したユーザーオブジェクトをセッションに保存 & ユーザーデータを更新）
        auth_login(request, user)

        # ログイン後処理（ログイン回数を増やしたりする。本来は user_logged_in シグナルを使えばもっと簡単に書ける）
        user.post_login()

        # ロギング
        logger.info("User(id={}) has logged in.".format(user.id))

        # フラッシュメッセージを画面に表示
        messages.info(request, "ログインしました。")

        # ショップ画面にリダイレクト
        return HttpResponseRedirect(reverse('shop:index'))


login = LoginView.as_view()


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # ロギング
            logger.info("User(id={}) has logged out.".format(request.user.id))
            # ログアウト処理
            auth_logout(request)

        # フラッシュメッセージを画面に表示
        messages.info(request, "ログアウトしました。")

        return HttpResponseRedirect(reverse('accounts:login'))


logout = LogoutView.as_view()


class ProfileChangeView(LoginRequiredMixin, UpdateView):
    form_class = ProfileChangeForm
    template_name = 'accounts/profile_change.html'
    success_url = '/accounts/profile_change/'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        # フラッシュメッセージを画面に表示
        messages.info(self.request, "プロフィールを変更しました。")
        return response


# class ProfileChangeView(LoginRequiredMixin, View):
#     def get(self, request, *args, **kwargs):
#         form = ProfileChangeForm(None, instance=request.user)
#         context = {
#             'form': form,
#         }
#         return TemplateResponse(request, 'accounts/profile_change.html', context)
#
#     def post(self, request, *args, **kwargs):
#         # フォームを使ってバリデーション
#         form = ProfileChangeForm(request.POST, request.FILES, instance=request.user)
#         if not form.is_valid():
#             context = {
#                 'form': form,
#             }
#             return TemplateResponse(request, 'accounts/profile_change.html', context)
#         # 変更を保存
#         form.save()
#         # フラッシュメッセージを画面に表示
#         messages.info(request, "プロフィール画像を変更しました。")
#         return HttpResponseRedirect('/accounts/profile/')


profile_change = ProfileChangeView.as_view()
