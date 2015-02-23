#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):
        user = self.model(
            email=self.normalize_email(email),
            is_active=True,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **kwargs):
        user = self.model(
            email=email,
            is_staff=True,
            is_superuser=True,
            is_active=True,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'email'
    class Meta:
        verbose_name = 'Użytkownik'
        verbose_name_plural = 'Użytkownicy'
    username = models.CharField(max_length=30, verbose_name='Nazwa użytkownika')
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()
    def get_discount(self):
        from amsoil.models import UserMeta
        if UserMeta.getValue(self,'discount'):
            return str(UserMeta.getValue(self,'discount')) + '%'
        else:
            return 'brak'
    def get_discount_end(self):
        from amsoil.models import UserMeta
        if UserMeta.getValue(self,'discount'):
            return str(UserMeta.getValue(self,'discount_ends'))
        else:
            return '-'
    get_discount.short_description = 'Zniżka'
    get_discount_end.short_description = 'Zniżka wygasa'
    REQUIRED_FIELDS = ['username']

    def get_full_name(self):
        return self.email
    def get_short_name(self):
        return self.email
