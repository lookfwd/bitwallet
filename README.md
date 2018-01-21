# BitWallet
A python module that provides a wallet that can do P&L

## Installation

Quick install/upgrade with `pip install --no-cache-dir -U bitwallet`

## Running

You can get your balances from any number of exchanges by doing: `PYTHONPATH=. bin/balances.py <your name>`. You should have a `<your name>.yaml` file with the following format:

```
-   name: <exchange name - should be a ccxt module>
    key: <key>
    secret: <secret>
    uid: <uid for exchanges that need it>
```

All the [ccxt exchanges](https://github.com/ccxt/ccxt/tree/master/python/ccxt) are supported.

## Notes

To release `python setup.py sdist`, `twine upload dist/*`.
