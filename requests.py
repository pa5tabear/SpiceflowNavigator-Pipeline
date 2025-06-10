class Response:
    def __init__(self, text='', status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

def get(url, timeout=5):
    return Response()
