import unittest

from bitwallet import *
from hypothesis import given, settings
from hypothesis.strategies import integers, booleans, tuples, lists


class TestWallet(unittest.TestCase):

    @given(booleans(), integers(min_value=1), integers(min_value=1))
    def test_basic_buy(self, auditable, q, price):
        wallet = Wallet(auditable)
        wallet.buy("btcbtc", q, price)
        assert wallet.total_coins() == {'btcbtc': q}
        assert wallet.total_coin('btcbtc') == q
        assert wallet.total_coin('unknown') == 0
        assert wallet.tickers == ['btcbtc']

    @given(booleans(), integers(min_value=1), integers(min_value=1))
    def test_basic_buy_sell_to_target(self, auditable, q, price):
        wallet = Wallet(auditable)
        wallet.buy("btcbtc", q, price)
        wallet.sell_to_target("btcbtc", q, price)
        assert wallet.total_coins() == {}
        assert wallet.total_coin('btcbtc') == 0
        assert wallet.tickers == []

    @given(booleans(), integers(min_value=1), integers(min_value=1),
           integers(min_value=1))
    def test_basic_buy_sell_all(self, auditable, q, price, new_price):
        wallet = Wallet(auditable)
        wallet.buy("btcbtc", q, price)
        assert wallet.total_coins() == {"btcbtc": q}
        assert wallet.total_coin('btcbtc') == q
        wallet.sell_all("btcbtc", new_price)
        assert wallet.total_coins() == {}
        assert wallet.total_coin('btcbtc') == 0
        assert wallet.tickers == []

    @given(booleans(), integers(min_value=1), integers(min_value=1),
           integers(min_value=1))
    def test_buy_multi_blocks(self, auditable, q1, q2, price):
        wallet = Wallet(auditable)
        wallet.buy("btcbtc", q1, price)
        wallet.buy("btcbtc", q2, price)
        assert wallet.total_coins() == {"btcbtc": q1 + q2}
        assert wallet.total_coin('btcbtc') == q1 + q2

    @given(booleans(),
           lists(tuples(integers(min_value=1), integers(min_value=1)),
                 min_size=1),
           integers(min_value=1))
    def test_buy_multi_blocks_and_compile_pnl(self, auditable, buy_orders,
                                              sell_all_price):
        wallet = Wallet(auditable)
        for q, p in buy_orders:
            wallet.buy("btcbtc", q, p)
        pnl = []
        def audit(q, p):
            pnl.append((sell_all_price - p) * q)
        wallet.sell_all("btcbtc", sell_all_price, audit)
        if not auditable:
            pnl == []
            return
        assert len(pnl) == len(buy_orders)
        for i, (q, p) in enumerate(buy_orders):
            assert pnl[i] == (sell_all_price- p) * q

    @given(booleans(),
           lists(tuples(integers(min_value=1), integers(min_value=1)),
                 min_size=1),
           integers(min_value=1),
           integers(min_value=1))
    def test_buy_multi_blocks_sell_to_target_and_compile_pnl(self, auditable,
                                                             buy_orders,
                                                             sell_q,
                                                             sell_all_price):
        wallet = Wallet(auditable)
        total_q = 0
        for q, p in buy_orders:
            wallet.buy("btcbtc", q, p)
            total_q += q

        assert total_q > 0
        sell_q = 1 + (0 if (total_q == 1) else (sell_q % (total_q - 1)))
        pnl = []
        def audit(q, p):
            pnl.append((sell_all_price - p) * q)
        wallet.sell_to_target("btcbtc", sell_q, sell_all_price, audit)
        if not auditable:
            pnl == []
            return

        expected_pnl = []
        for q, p in buy_orders:
            if sell_q > 0:
                actual_sell = min(sell_q, q)
                expected_pnl.append(actual_sell * (sell_all_price - p))
                sell_q -= actual_sell
            else:
                break

        assert pnl == expected_pnl
