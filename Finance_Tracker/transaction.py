class Transaction:
    def __init__(self, date: str, amount: float, description: str, category: str):
        self.date = date
        self.amount = amount
        self.description = description
        self.category = category

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "amount": self.amount,
            "description": self.description,
            "category": self.category
        }