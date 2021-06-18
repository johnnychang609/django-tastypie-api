from tastypie.utils import trailing_slash
from django.conf.urls import url


class Endpoint:

    def __init__(self, *args, **kwargs):
        self.route = kwargs.pop("route", None)
        self.name = kwargs.pop("name", None)
        self.controller = None

    def __call__(self, func):
        func.name = self.name or "api_" + func.__name__
        func.route = self.route or func.__name__
        func.is_endpoint = True
        return func


def prepend_urls(self):
    urls = []
    if hasattr(self, 'endpoints'):
        for endpoint in self.endpoints:
            pattern = r"^(?P<resource_name>{resource})/{pattern}{endslash}$".format(
                resource=self._meta.resource_name,
                pattern=endpoint.get('route'),
                endslash=trailing_slash())
            urls.append(url(pattern, self.wrap_view(endpoint.get('controller')), name=endpoint.get('name')))
    return urls


def DiscoverEndpoints(resource):

    if not hasattr(resource, 'endpoints'):
        resource.endpoints = []

    for method, controller in vars(resource).items():

        if not hasattr(controller, 'is_endpoint'):
            continue

        resource.endpoints.append({
            "route": getattr(controller, 'route'),
            "name": getattr(controller, 'name'),
            "controller": getattr(controller, 'controller', method)
        })

    resource.prepend_urls = prepend_urls

    return resource