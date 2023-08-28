class Product:
    def __init__(self, code, description, price, ean_13) -> None:
        self.code = code
        self.description = description
        self.price = price
        self.ean_13 = ean_13
        self.qnt = 1

    def include_more(self):
        self.qnt += 1