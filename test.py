class TestDevice:
    def __init__(self, cf):
        self.type = cf.get('device_test_type', 'test')
        self.host = 'test'

    def auth(self):
        pass

    def check_temperature(self):
        return 23.5

    def send_data(self, data):
        pass
