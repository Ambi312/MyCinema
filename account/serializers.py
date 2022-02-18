# from django.contrib.auth import authenticate
# from rest_framework import serializers
#
# from .models import MyUser
# from .utils import send_activation_code
#
#
# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(min_length=6, write_only=True)
#     password_confirm = serializers.CharField(min_length=6, write_only=True)
#
#     class Meta:
#         model = MyUser
#         fields = ('email', 'password', 'password_confirm')
#
#     def validate(self, validated_data):
#         validated_data.get('password')
#         password = validated_data.get('password')
#         password_confirm = validated_data.get('password_confirm')
#         if password != password_confirm:
#             raise serializers.ValidationError('Passwords do not match!')
#         return validated_data
#
#     def create(self, validated_data):
#         email = validated_data.get('email')
#         password = validated_data.get('password')
#         user = MyUser.objects.create_user(email=email, password=password)
#         send_activation_code(email=user.email, activation_code=user.activation_code)
#         return user
#
#
# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(
#         label='Password',
#         style={'input_type': 'password'},
#         trim_whitespace=False
#     )
#
#     def validate(self, attrs):
#         email = attrs.get('email')
#         password = attrs.get('password')
#
#         if email and password:
#             user = authenticate(request=self.context.get('request'), email=email, password=password)
#
#             if not user:
#                 message = 'Unable to log in with'
#                 raise serializers.ValidationError(message, code='authorization')
#
#         else:
#             message = 'Must include email and password'
#             raise serializers.ValidationError(message, code='authorization')
#
#         attrs['user'] = user
#         return attrs

from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from rest_framework import serializers

from .utils import send_activation_mail

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    name = serializers.CharField(required=False)
    password = serializers.CharField(required=True, min_length=6)
    password_confirmation = serializers.CharField(required=True, min_length=6)

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Адрес почты уже занят')
        return email

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirmation = attrs.pop('password_confirmation')
        if password != password_confirmation:
            raise serializers.ValidationError('Пароли не совпадают')
        return attrs

    def create(self):
        attrs = self.validated_data
        user = User.objects.create_user(**attrs)
        code = user.generate_activation_code()
        send_activation_mail.delay(user.email, code)
        return user


class ActivationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(min_length=8, max_length=8)

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь не зарегистрирован')
        return email

    def validate_code(self, code):
        if not User.objects.filter(activation_code=code).exists():
            raise serializers.ValidationError('Пользователь не зарегистрирован')
        return code

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')
        if not User.objects.filter(email=email,
                                   activation_code=code).exists():
            raise serializers.ValidationError('Пользователь не найден')
        return attrs

    def activate(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        user.is_active = True
        user.activation_code = ''
        user.save()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь не зарегистрирован')
        return email

    def validate(self, attrs):
        request = self.context.get('request')
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            user = authenticate(username=email,
                                password=password,
                                request=request)
            if not user:
                raise serializers.ValidationError('Неверный email или пароль')
        else:
            raise serializers.ValidationError('Email и пароль обязательны')
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_pass = serializers.CharField(required=True)
    password = serializers.CharField(required=True, min_length=6)
    password_confirm = serializers.CharField(required=True, min_length=6)

    def validate_old_pass(self, old_pass):
        user = self.context.get('request').user
        if not user.check_password(old_pass):
            raise serializers.ValidationError('Неверный пароль')
        return old_pass

    def validate(self, attrs):
        pass1 = attrs.get('password')
        pass2 = attrs.get('password_confirm')
        if pass1 != pass2:
            raise serializers.ValidationError('Пароли не совпадают')
        return attrs

    def set_new_pass(self):
        user = self.context.get('request').user
        password = self.validated_data.get('password')
        user.set_password(password)
        user.save()


# class ForgotPasswordSerializer(serializers.Serializer):
#     email = serializers.EmailField(required=True)
#
#     def validate_email(self, email):
#         if not User.objects.filter(email=email).exists():
#             raise serializers.ValidationError('Пользователь не зарегистрирован')
#         return email
#
#     def send_new_pass(self):
#         email = self.validated_data.get('email')
#         user = User.objects.get(email=email)
#         random_pass = get_random_string(15)
#         user.set_password(random_pass)
#         user.save()
#         send_mail('Восстановление пароля',
#                   f'Ваш новый пароль: {random_pass}',
#                   'test@gmail.com',
#                   [email])


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь не зарегистрирован')
        return email

    def send_code(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        user.generate_activation_code()
        send_mail(
            'Восстановление пароля',
            f'Ваш код подтверждения: {user.activation_code}',
            'test@gmail.com',
            [email]
        )


class ForgotPasswordCompleteSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(min_length=8, max_length=8, required=True)
    password = serializers.CharField(required=True)
    password_confirm = serializers.CharField(required=True)

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь не зарегистрирован')
        return email

    def validate_code(self, code):
        if not User.objects.filter(activation_code=code).exists():
            raise serializers.ValidationError('Пользователь не зарегистрирован')
        return code

    def validate(self, attrs):
        pass1 = attrs.get('password')
        pass2 = attrs.get('password_confirm')
        if pass1 != pass2:
            raise serializers.ValidationError('Пароли не совпадают')
        return attrs

    def set_new_pass(self):
        email = self.validated_data.get('email')
        password = self.validated_data.get('password')
        user = User.objects.get(email=email)
        user.set_password(password)
        user.activation_code = ''
        user.save()

