class Service:
    def __init__(self, name, endpoint, health_check=None):
        self.name = name
        self.endpoint = endpoint
        self.health_check = health_check or (lambda: True)

class ServiceRegistry:
    def __init__(self):
        self.services = {}

    def register(self, service: Service):
        self.services[service.name] = service

    def get_service(self, name):
        return self.services.get(name)

    def health_report(self):
        report = {}
        for name, service in self.services.items():
            report[name] = service.health_check()
        return report
