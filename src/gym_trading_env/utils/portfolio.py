class Portfolio:
    def __init__(self, asset, fiat, interest_asset=0, interest_fiat=0):
        self.asset = asset
        self.fiat = fiat
        self.interest_asset = interest_asset
        self.interest_fiat = interest_fiat

    def valorisation(self, price):
        return sum([
            self.asset * price,
            self.fiat,
            - self.interest_asset * price,
            - self.interest_fiat
        ])

    def real_position(self, price):
        return (self.asset - self.interest_asset) * price / self.valorisation(price)

    def position(self, price):
        return self.asset * price / self.valorisation(price)

    def settle_interest(self):
        self.asset -= self.interest_asset
        self.interest_asset = 0
        self.fiat -= self.interest_fiat
        self.interest_fiat = 0

    def trade_to_position(self, position, price, trading_fees):
        current_position = self.position(price)
        if current_position == position:
            return
        assert price > 0, "Price must be greater than zero"
        relative_value = self.valorisation(price) / price
        if position > current_position:
            fiat_cost_factor = 1 + trading_fees
            cost_position = 1 + position * trading_fees
        else:
            fiat_cost_factor = 1 - trading_fees
            cost_position = 1 - position * trading_fees
        asset_trade = (relative_value * position - self.asset) / cost_position
        self.fiat -= asset_trade * price * fiat_cost_factor
        self.asset += asset_trade

    def update_interest(self, borrow_interest_rate):
        self.interest_asset = max(0, - self.asset) * borrow_interest_rate
        self.interest_fiat = max(0, - self.fiat) * borrow_interest_rate

    def __str__(self):
        return f"{self.__class__.__name__}({self.__dict__})"

    def describe(self, price):
        print("Value : ", self.valorisation(price), "Position : ", self.position(price))

    def get_portfolio_distribution(self):
        return {
            "asset": max(0, self.asset),
            "fiat": max(0, self.fiat),
            "borrowed_asset": max(0, -self.asset),
            "borrowed_fiat": max(0, -self.fiat),
            "interest_asset": self.interest_asset,
            "interest_fiat": self.interest_fiat,
        }


class TargetPortfolio(Portfolio):
    def __init__(self, position, value, price):
        super().__init__(
            asset=position * value / price,
            fiat=(1 - position) * value,
            interest_asset=0,
            interest_fiat=0
        )
