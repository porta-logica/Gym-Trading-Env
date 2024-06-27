from unittest import TestCase
from portfolio import Portfolio


class TestPortfolio(TestCase):

    def test_trade_to_position_1_0(self):
        portfolio = Portfolio(asset=0, fiat=1000)
        price = 10.0
        trading_fees = 0.1
        self.assertEqual(portfolio.valorisation(price), 1000)

        # open a position of 1.0 <- 0.0
        #   buy asset of x units at a price of 10.0 each; for a total budget of 1000.0
        #   the total cost is x * 10 * 0.1 = x
        #   the total amount is x * 10.0 + x * x = 11 * x is paid from fiat
        #   the portfolio value decreases by the trading costs x
        #   get an asset of x = 1000.0 / 11.0 = 90.91 units
        portfolio.trade_to_position(position=1.0, price=price, trading_fees=trading_fees)

        self.assertEqual(portfolio.position(price), 1.0)
        self.assertEqual(round(portfolio.valorisation(price), 2), 909.09)
        self.assertEqual(round(portfolio.asset, 2), 90.91)

    def test_trade_to_position_0_0(self):
        portfolio = Portfolio(asset=100, fiat=0.0)
        price = 10.0
        trading_fees = 0.1
        self.assertEqual(portfolio.position(price), 1.0)
        self.assertEqual(portfolio.valorisation(price), 1000)

        # close a position of 1.0 -> 0.0
        #   the asset is 100 units; no fiat money
        #   the portfolio value is 100 * 10.0 = 1000.0
        #   the trading cost is 0.1 * 1000.0 = 100.0
        #   the portfolio value decreases by the trading costs
        #   get an asset of 0 units and fiat money of 900.0
        portfolio.trade_to_position(position=0.0, price=price, trading_fees=trading_fees)

        self.assertEqual(portfolio.position(price), 0.0)
        self.assertEqual(portfolio.valorisation(price), 900)
        self.assertEqual(portfolio.asset, 0)

    def test_trade_to_position_0_5(self):
        portfolio = Portfolio(asset=100, fiat=0.0)
        price = 10.0
        trading_fees = 0.1
        self.assertEqual(portfolio.position(price), 1.0)
        self.assertEqual(portfolio.valorisation(price), 1000)

        # reduce a position of 1.0 -> 0.5
        #   the asset is 100 units; no fiat money
        #   the portfolio value is 100 * 10.0 = 1000.0
        #   sell an asset of x units at a price of 10.0, x > 0
        #   the trading cost is x * 10.0 * 0.1 = x
        #   the portfolio value decreases by the trading costs
        #   get an asset of (100 - x) units
        #   the fiat money is x * 10.0 * (1 - 0.1) = 9 * x
        #   the portfolio value is (100 - x) * 10.0 + 9 * x = 1000 - x
        #   solve the equation 2 * (100 - x) * 10.0 = 1000 - x
        #   x * 19 = 1000 -> x = 1000 / 19 = 52.6315
        #   Results:
        #       asset = 47.3684
        #       fiat  = 473.6844
        #   the portfolio value is 1000 - x = 947.37
        portfolio.trade_to_position(position=0.5, price=price, trading_fees=trading_fees)

        self.assertEqual(round(portfolio.position(price), 2), 0.5)
        self.assertEqual(round(portfolio.asset, 2), 47.37)
        self.assertEqual(round(portfolio.fiat, 2), 473.68)
        self.assertEqual(round(portfolio.valorisation(price), 2), 947.37)

    def test_trade_to_position_minus_0_5(self):
        portfolio = Portfolio(asset=50, fiat=500.0)
        price = 10.0
        trading_fees = 0.1
        interest_rate = 0.1
        self.assertEqual(portfolio.position(price), 0.5)
        self.assertEqual(portfolio.valorisation(price), 1000.0)

        # reduce position from 0.5 to -0.5
        #   the asset is 50 units; fiat money is 500.0
        #   the portfolio value is 50 * 10.0 + 500.0 = 1000.0
        #   short sell an asset of x units at a price of 10.0, x > 0
        #   the trading cost is x * 10.0 * 0.1 = x
        #   the portfolio value decreases by the trading costs
        #   get an asset of (50 - x) units
        #   the fiat money is 500.0 + x * 10.0 * (1 - 0.1) = 500.0 + 9 * x
        #   the portfolio value is (50 - x) * 10.0 + 500.0 + 9 * x = 1000.0 - x
        #   solve the equation (50 - x) * 10.0 = -0.5 * (1000.0 - x)
        #   x = (500.0 + 0.5 * 1000.0) / (10.0 + 0.5) = 95.24
        #   Results:
        #       asset = -45.24
        #       fiat  = 1357.14
        #   the portfolio value is 1000 - x = 904.76
        portfolio.trade_to_position(position=-0.5, price=price, trading_fees=trading_fees)

        self.assertEqual(round(portfolio.position(price), 2), -0.5)
        self.assertEqual(round(portfolio.asset, 2), -45.24)  # borrowed asset = 45.24
        self.assertEqual(round(portfolio.fiat, 2), 1357.14)
        self.assertEqual(round(portfolio.valorisation(price), 2), 904.76)
        #   interest_asset is (50 - x) * 10.0 * interest_rate * -1
        portfolio.update_interest(borrow_interest_rate=interest_rate)
        self.assertEqual(round(portfolio.interest_asset, 2), 4.52)
        self.assertEqual(round(portfolio.interest_fiat, 2), 0.0)

    def test_settle_interest(self):
        portfolio = Portfolio(asset=-50, fiat=1600.0, interest_asset=10)
        price = 10.0
        trading_fees = 0.1
        interest_rate = 0.1
        self.assertEqual(portfolio.position(price), -0.5)
        self.assertEqual(portfolio.valorisation(price), 1000.0)
        portfolio.settle_interest()
        self.assertEqual(portfolio.valorisation(price), 1000.0)
        self.assertEqual(portfolio.position(price), -0.6)

    def test_trade_from_position_minus_0_5(self):
        portfolio = Portfolio(asset=-50, fiat=1500.0)
        price = 10.0
        trading_fees = 0.1
        interest_rate = 0.1
        self.assertEqual(portfolio.valorisation(price), 1000.0)
        self.assertEqual(portfolio.position(price), -0.5)

        # increase position from -0.5 to 0.5
        #   the borrowed asset is 50 units; fiat money is 1500.0
        #   the portfolio value is (-50) * 10.0  + 1500.0 = 1000.0
        #   close short position by buying x units at a price of 10.0, x > 0
        #   the trading cost is x * 10.0 * 0.1 = x
        #   the portfolio value decreases by the trading costs
        #   get an asset of x - 50 units
        #   the fiat money is 1500.0 - 10.0 * x - x = 1500.0 - 11 * x
        #   the portfolio value is (x - 50) * 10.0 + 1500.0 - 11 * x = 1000.0 - x
        #   solve the equation (x - 50) * 10.0 = 0.5 * (1000.0 - x)
        #   x = 1500.0 / 2 * (10.0 + 0.5) = 94.74
        #   Results:
        #       asset = 44.74
        #       fiat  = 447.37
        #   the portfolio value is 447.4 + 547.37 = 894.74
        portfolio.trade_to_position(position=0.5, price=price, trading_fees=trading_fees)
        self.assertEqual(round(portfolio.asset, 2), 45.24)
        self.assertEqual(round(portfolio.fiat, 2), 452.38)
        self.assertEqual(round(portfolio.valorisation(price), 2), 904.76)
        portfolio.update_interest(borrow_interest_rate=interest_rate)
        self.assertEqual(round(portfolio.interest_asset, 2), 0.0)
        self.assertEqual(round(portfolio.interest_fiat, 2), 0.0)
