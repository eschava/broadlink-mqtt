# noinspection PyMethodMayBeStatic
class TestDevice:
    def __init__(self, cf):
        self.type = cf.get('device_test_type', 'test')
        self.host = ('test', 80)
        self.mac = [1, 2, 3, 4, 5, 6]

    def auth(self):
        pass

    def check_temperature(self):
        return 23.5

    def send_data(self, data):
        pass

    def check_sensors(self):
        return {'temperature': 23.5, 'humidity': 36, 'light': 'dim', 'air_quality': 'normal', 'noise': 'noisy'}

    def check_sensors_raw(self):
        return {'temperature': 23.5, 'humidity': 36, 'light': 1, 'air_quality': 3, 'noise': 2}
