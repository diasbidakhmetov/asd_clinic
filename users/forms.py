from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from scripts.get_iin import get_full_date
from users.models import User, Gender, UserRole


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'field', 'placeholder': 'ЖСН'}
        ),
        label="IIN"
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'field', 'placeholder': 'Құпиясөз'}
        )
    )

    class Meta:
        model = User
        fields = ('username', 'password')


class UserRegisterForm(UserCreationForm):
    iin = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'field', 'placeholder': 'ЖСН'}
        )
    )

    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'field', 'placeholder': 'Тегі'}
        )
    )

    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'field', 'placeholder': 'Аты'}
        )
    )

    father_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'field', 'placeholder': 'Әкесінің аты'}
        )
    )

    gender = forms.ModelChoiceField(
        queryset=Gender.objects.all(),
        widget=forms.Select(attrs={'class': 'field'})
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'field', 'placeholder': 'Құпиясөз'}
        )
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'field', 'placeholder': 'Құпиясөзді растау'}
        )
    )

    class Meta:
        model = User
        fields = (
            'iin',
            'last_name',
            'first_name',
            'father_name',
            'gender',
            'password1',
            'password2'
        )

    def clean_iin(self):
        iin = self.cleaned_data.get('iin')

        if not iin:
            raise forms.ValidationError("Введите ИИН.")

        try:
            b_day = get_full_date(str(iin))
        except Exception:
            raise forms.ValidationError(
                "Некорректный ИИН. Невозможно вычислить дату рождения."
            )

        self.cleaned_data['b_day'] = b_day
        return iin

    def save(self, commit=True):
        user = super().save(commit=False)

        user.b_day = self.cleaned_data['b_day']

        # Обычная регистрация = всегда Қолданушы
        user.role = UserRole.objects.get(name='Қолданушы')

        if commit:
            user.save()

        return user


class StaffUserRegisterForm(UserRegisterForm):
    role = forms.ModelChoiceField(
        queryset=UserRole.objects.all(),
        widget=forms.Select(attrs={'class': 'field'}),
        empty_label=None
    )

    class Meta(UserRegisterForm.Meta):
        fields = UserRegisterForm.Meta.fields + ('role',)

    def save(self, commit=True):
        user = super().save(commit=False)

        # Здесь роль берётся из выбора сотрудника
        user.role = self.cleaned_data['role']

        if commit:
            user.save()

        return user