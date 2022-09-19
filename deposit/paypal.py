import sys

from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment


class PayPalClient:
    def __init__(self):
        self.client_id = "AYH2KI_u3dPqd9NFjP_oVslrHIOW2JevO9iYvmAyIufhT-Ky_5VxRuPxQQmDuWLSAps5EZJ_BFP5aXSG"
        self.client_secret = "EHskP6ffRai4VC0h4ZTaL4e1oSms2sK7Nga4PTotV25OU49m4LDCSjVyQUyCtTrqteNgcG6efKdbPw7v"
        self.environment = SandboxEnvironment(client_id=self.client_id, client_secret=self.client_secret)
        self.client = PayPalHttpClient(self.environment)