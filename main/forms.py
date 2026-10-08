from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile, Reservation


class RegisterForm(UserCreationForm):
    """Форма регистрации нового пользователя."""
    email = forms.EmailField(
        label='Email',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'})
    )
    first_name = forms.CharField(
        label='Имя',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иван'})
    )
    last_name = forms.CharField(
        label='Фамилия',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов'})
    )
    phone = forms.CharField(
        label='Телефон',
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (900) 000-00-00'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Стилизуем стандартные поля
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Логин (латиница, без пробелов)',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Пароль (минимум 8 символов)',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Повторите пароль',
        })
        # Русские подписи
        self.fields['username'].label = 'Логин'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email', '')
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
            # Профиль создаётся автоматически сигналом, но обновим телефон
            profile = user.profile
            profile.phone = self.cleaned_data.get('phone', '')
            profile.save()
        return user


class LoginForm(AuthenticationForm):
    """Форма входа с Bootstrap-стилями."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Логин',
            'autofocus': True,
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Пароль',
        })
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'


class ProfileForm(forms.ModelForm):
    """Редактирование профиля."""
    class Meta:
        model = Profile
        fields = ('phone',)
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (900) 000-00-00',
            }),
        }
        labels = {
            'phone': 'Телефон',
        }


class ReservationForm(forms.ModelForm):
    """Форма бронирования лекарства."""
    class Meta:
        model = Reservation
        fields = ('quantity', 'comment')
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1,
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Например: «Буду после 18:00» или «Нужен срочно»',
            }),
        }
        labels = {
            'quantity': 'Количество',
            'comment': 'Комментарий (необязательно)',
        }

    def __init__(self, *args, stock=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.stock = stock
        if stock:
            # Ограничиваем количество тем, что есть в наличии
            self.fields['quantity'].widget.attrs['max'] = stock.quantity
            self.fields['quantity'].help_text = f'В наличии: {stock.quantity} шт.'

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if self.stock and quantity > self.stock.quantity:
            raise forms.ValidationError(
                f'В аптеке только {self.stock.quantity} шт. Уменьшите количество.'
            )
        if quantity < 1:
            raise forms.ValidationError('Количество должно быть не менее 1.')
        return quantity