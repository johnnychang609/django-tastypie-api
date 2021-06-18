from django.db import models
from django.utils import timezone
from exercise.settings import MEDIA_ROOT


# Create your models here.

class product(models.Model): # 產品列表
    product_id = models.AutoField(primary_key=True) #商品id
    stock_pcs = models.IntegerField('商品庫存數量') #商品庫存數量
    price = models.IntegerField('商品價格') #商品單價
    shop_id =  models.CharField('商品所屬館別',max_length=20,blank=True,null=True) # 商品所屬館別
    vip = models.BooleanField(default=False)  # True ( VIP限定 ) / False  ( 無限制購買對象 )
    created = models.DateTimeField(default=timezone.now)
   
    class Meta:
        verbose_name = 'product '
    def __str__(self):
            return self.product_id

class order(models.Model): # 訂單資料
    order_id = models.AutoField(primary_key=True) #訂單id 
    product_id=models.ForeignKey(product, on_delete=models.CASCADE, blank=True, null=True) # 商品id
    qty = models.IntegerField('購買數量') #購買數量
    customer_id =  models.CharField('客戶ID',max_length=20,blank=True,null=True) # 訂單所屬客戶ID
    created = models.DateTimeField(default=timezone.now)
   
    class Meta:
        verbose_name = 'order '
    def __str__(self):
            return self.order_id

