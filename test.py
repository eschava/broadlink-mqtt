# noinspection PyMethodMayBeStatic
class TestDevice:
    def __init__(self, cf):
        self.type = cf.get('device_test_type', 'test')
        self.host = ('test', 80)
        self.mac = [1, 2, 3, 4, 5, 6]

    def auth(self):
        pass

    # RM2/RM4
    def check_temperature(self):
        return 23.5

    # RM4
    def check_humidity(self):
        return 56

    def enter_learning(self):
        pass

    def check_data(self):
        payload = bytearray(5)
        payload[0] = 0xAA
        payload[1] = 0xBB
        payload[2] = 0xCC
        payload[3] = 0xDD
        payload[4] = 0xEE
        return payload

    def send_data(self, data):
        pass

    def check_sensors(self):
        return {'temperature': 23.5, 'humidity': 36, 'light': 'dim', 'air_quality': 'normal', 'noise': 'noisy'}

    def check_sensors_raw(self):
        return {'temperature': 23.5, 'humidity': 36, 'light': 1, 'air_quality': 3, 'noise': 2}

    def get_percentage(self):
        return 33

    def open(self):
        pass

    def get_state(self):
        return {'pwr': 1, 'pwr1': 1, 'pwr2': 0, 'maxworktime': 60, 'maxworktime1': 60, 'maxworktime2': 0, 'idcbrightness': 50}

    def check_power(self):
        return {'s1': True, 's2': False, 's3': True, 's4': False}
