from context import netparse


def test_nexus_table():
    f = open('tests/data/nexus_int_status.txt')

    print(netparse.get(f.read()))