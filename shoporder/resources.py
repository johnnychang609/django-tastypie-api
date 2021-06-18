from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseRedirect,
)
from .models import product,order
from .mixins import Endpoint,DiscoverEndpoints
from functools import wraps

@DiscoverEndpoints
class ProductResource(ModelResource):
    class Meta:
        queryset = product.objects.all()
        allowed_methods  = ['get', 'post', 'put', 'delete']
        resource_name = 'product'
        authentication = Authentication()
        authorization = Authorization()

@DiscoverEndpoints
class OrderResource(ModelResource):
    product_id = fields.ToOneField('shoporder.resources.ProductResource', 'product_id', full=True) 
    class Meta:
        queryset = order.objects.select_related('product_id').all().order_by('qty')
        allowed_methods  = ['get', 'post', 'put', 'delete']
        resource_name = 'order'
        fields = ['order_id', 'product_id','qty','customer_id','stock_pcs','price','shop_id','vip']  #設定顯示欄位
        authentication = Authentication()
        authorization = Authorization()

    @Endpoint()
    def Cvip(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        data = self.deserialize(request, request.body,format=request.META.get('CONTENT_TYPE', 'application/json'))
        vip = data.get('vip','')
        pcs = data.get('pcs','')
        Pid = data.get('Pid','')
        rs = product.objects.get(product_id=Pid) 
        obj={"vipstate":False,"pcstate":False,"viprs":'',"pcsrs":''}
        if rs.vip and vip: # 身分是 vip 商品也是 VIP
            if rs.stock_pcs>= int(pcs): # vip 商頻品數量足夠
                obj['vipstate']=True
                obj['pcstate']=True
                obj['viprs']='This is vip'
                obj['pcsrs']= 'PCS is enough'           
            else: # vip 商品數量不足
                obj['vipstate']=True
                obj['pcstate']= False
                obj['viprs']='This is vip'
                obj['pcsrs']='PCS is not enough'   
        else:
            if rs.stock_pcs>= int(pcs): # 非 vip 商頻品數量足夠    
                obj['vipstate']=False
                obj['pcstate']=True
                obj['viprs']='This is not vip'
                obj['pcsrs']='PCS is enough'   
            else: # 非vip 商品數量不足
                obj['vipstate']=False
                obj['pcstate']=False
                obj['viprs']='This is not vip'
                obj['pcsrs']='PCS is not enough'                   
        
        return self.create_response(request,obj, HttpResponse)  

    @Endpoint()
    def Dorder(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        data = self.deserialize(request, request.body,format=request.META.get('CONTENT_TYPE', 'application/json'))
        Pid = data.get('Pid','')  
        pcs = data.get('pcs','')
        rs = product.objects.get(product_id=Pid)
        obj={"qty":False,"qtystate":''}
        if rs.stock_pcs<int(pcs): # 訂單數量大於可訂購數量
            obj['qtystate'] = '貨源不足'
        else:
            obj['qty'] = True
            obj['qtystate'] = '商品到貨'
        return self.create_response(request,obj, HttpResponse) 


    @Endpoint()
    def putorder(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        data = self.deserialize(request, request.body,format=request.META.get('CONTENT_TYPE', 'application/json'))
        customerid = data.get('customer_id','')  
        aount = data.get('qty','')  
        productid = data.get('product_id','')
        rs = product.objects.get(product_id=productid)
        ps = order(product_id=rs,qty=int(aount),customer_id=customerid)
        ps.save()
        qtys = int(rs.stock_pcs) - int(aount)
        product.objects.filter(product_id=productid).update(stock_pcs=int(qtys))    
        obj={"success":True,"state":'更新成功'}
        return self.create_response(request,obj, HttpResponse)  

    @Endpoint()
    def delorder(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        data = self.deserialize(request, request.body,format=request.META.get('CONTENT_TYPE', 'application/json'))
        orderid = data.get('orderid','')  
        aount = data.get('qty','')  
        productid = data.get('Pid','')
        rs = product.objects.get(product_id=productid)
        qtys = int(rs.stock_pcs) + int(aount)
        product.objects.filter(product_id=productid).update(stock_pcs=int(qtys))   
        order.objects.filter(order_id=orderid).delete()
        obj={"success":True,"state":'更新成功'}
        return self.create_response(request,obj, HttpResponse)          
     

product_resource = ProductResource()
order_resource = OrderResource()