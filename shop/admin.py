from django import forms
from django.contrib import admin

from .models import Author, Book, Publisher


class BookAdminForm(forms.ModelForm):
    def clean_title(self):
        value = self.cleaned_data['title']
        if 'Django' not in value:
            raise forms.ValidationError(
                "タイトルには「Django」という文字を含めてください")
        return value


class BookAdmin(admin.ModelAdmin):
    # 一覧画面の表示フィールドを変更
    list_display = ('title', 'publisher', 'price')
    # 一覧画面のソート順を変更
    ordering = ('-price',)
    # 変更画面の表示フィールドを変更
    # fields = ('title', 'publisher', 'authors', 'price')
    # フォームを入れ替える
    form = BookAdminForm


admin.site.register(Publisher)
admin.site.register(Author)
admin.site.register(Book, BookAdmin)
