from django.db import models
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel

# Create your models here.
class User(AbstractUser, BaseModel):
    '''用户模型类'''
    points = models.IntegerField(default=0, verbose_name='用户积分')

    class Meta:
        db_table = 'fd_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class AddressManager(models.Manager):
    '''用户地址模型管理器'''

    # 获取用户的默认收获地址
    def get_default_address(self, user):
        try:
            address = self.get(user=user, is_default=True)
        except self.model.DoesNotExist:
            address = None

        return address


class Address(BaseModel):
    '''用户地址信息模型类'''
    user = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='所属用户')
    receiver = models.CharField(max_length=20, verbose_name='收件人')
    address = models.CharField(max_length=256, verbose_name='收件地址')
    zip_code = models.CharField(max_length=6, null=True, verbose_name='邮政编码')
    phone = models.CharField(max_length=11, verbose_name='联系电话')
    is_default = models.BooleanField(default=False, verbose_name='是否为默认地址')

    # 自定义模型管理其类
    objects = AddressManager()

    class Meta:
        db_table = 'fd_address'
        verbose_name = '收获地址'
        verbose_name_plural = verbose_name

