#!/opt/check_dus/bin/python
"""Hello world Nagios check."""
import argparse
from nagiosplugin.result import Result
from nagiosplugin.state import Ok, Critical
import hashlib
import nagiosplugin
import requests


class Equal(nagiosplugin.Context):

    def __init__(self, name, expect, result_cls=Result):
        super(Equal, self).__init__(name, None, result_cls)
        self.expect = expect

    def evaluate(self, metric, resource):
        result = Ok if metric.value == self.expect else Critical
        return self.result_cls(result, metric=metric)

    def describe(self, metric):
        # XXX no idea how to get this working
        return 'got {}, expected {}'.format(metric.value, self.expect)


class DUSSIPStatus(nagiosplugin.Resource):

    def probe(self):
        r = requests.get('http://www.dus.net/dusicon.php?a=cb153503a1eb68a52d7d1e0980ac53dd')
        m = hashlib.md5()
        m.update(r.content)
        return [nagiosplugin.Metric('status_hash', m.hexdigest(), context='account_status')]


@nagiosplugin.guarded
def main():
    argp = argparse.ArgumentParser()
    argp.add_argument('-v', '--verbose', action='count', default=0)
    args = argp.parse_args()
    check = nagiosplugin.Check(
        DUSSIPStatus(),
        Equal('account_status', '9385bc51ed8b0e054a87000dd09cc28e'))
    check.main(args.verbose)


if __name__ == '__main__':
    main()
