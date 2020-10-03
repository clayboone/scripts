import argparse
import logging
import sys

import requests

_log = logging.getLogger(__name__)

LIST_OF_VPNS_URL = "https://raw.githubusercontent.com/ejrv/VPNs/master/vpn-ipv4.txt"


class Subnet:
    """A subnet of the internet as determined by a network address and its
    variable-length subnet mask.

    >>> subnet = Subnet("1.2.3.0/24")
    >>> assert "1.2.3.123" in subnet

    If the mask is omitted, it is assumed to be /32.
    """
    def __init__(self, subnet_address):
        if "/" not in subnet_address:
            subnet_address += "/"

        address, mask = subnet_address.split("/")

        self._first_address = address
        self._last_address = self._get_last_address(address, mask)

    def __contains__(self, ip):
        return self._ip_as_int(ip) in range(self.first_address, self.last_address + 1)

    @property
    def first_address(self):
        "The first IPv4 address in this subnet."
        return self._ip_as_int(self._first_address)

    @property
    def last_address(self):
        "The last IPv4 address in this subnet."
        return self._ip_as_int(self._last_address)

    @staticmethod
    def _ip_as_int(ip_value: str) -> int:
        assert isinstance(ip_value, str)
        assert "/" not in ip_value
        assert len(ip_value.split(".")) == 4

        octet1, octet2, octet3, octet4 = [int(n) for n in ip_value.split(".")]
        return octet1 << 24 | octet2 << 16 | octet3 << 8 | octet4 << 0

    @staticmethod
    def _int_as_ip(ip_value: int) -> str:
        assert isinstance(ip_value, int)

        MAX_IPV4 = 255 << 24 | 255 << 16 | 255 << 8 | 255
        assert 0 < ip_value <= MAX_IPV4

        return ".". join([str(int(n, 2)) for n in [format(ip_value, "032b")[i:i+8] for i in range(0, 32, 8)]])

    @classmethod
    def _get_last_address(cls, network_address: str, mask: str):
        if not mask or int(mask) > 31:
            return network_address

        inverted_bits = [not bool(int(bit)) for bit in '1'*int(mask) + '0'*(32-int(mask))]
        wildcard_mask = int("".join([str(int(bit)) for bit in inverted_bits]), 2)

        return cls._int_as_ip(cls._ip_as_int(network_address) | wildcard_mask)


def _test_vpncheck():
    "Unit test this module."
    logging.basicConfig(level=logging.INFO)
    _log.info("Running internal test.")

    known_vpn_subnets = [
        "1.242.79.148",
        "2.56.16.0/22",
    ]

    vpn_subnets = [Subnet(subnet) for subnet in known_vpn_subnets]

    clients = [
        {"name": "Copper",        "ip": "2.56.15.254"},   # no vpn
        {"name": "Tod",           "ip": "2.56.20.1"},     # no vpn
        {"name": "Monty Pasta",   "ip": "2.56.16.2"},     # vpn
        {"name": "Danger Noodle", "ip": "2.56.19.254"},   # vpn
        {"name": "Nope Rope",     "ip": "1.242.79.148"},  # vpn
    ]

    for client in clients:
        client_name, client_ip = client.values()

        if any(client_ip in subnet for subnet in vpn_subnets):
            _log.info("%s is using a VPN!", client_name)
            continue

        _log.info("%s might not be using a VPN...", client_name)


def main():
    "Command line entry point."
    if "--test" in sys.argv:
        _test_vpncheck()
        return

    parser = argparse.ArgumentParser(description="Determine if an ip address is using a VPN.")
    parser.add_argument("ip_address", type=str, help="ip address to check")
    parser.add_argument("--verbose", action="store_true", help="be noisy")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    _log.info("Fetching list of VPNs.")
    try:
        with requests.get(LIST_OF_VPNS_URL) as response:
            lines = response.content.decode().splitlines()
    except requests.ConnectionError as exc:
        _log.error("Failed to download VPN list: %s", exc)
        return

    list_of_vpns = [line.strip() for line in lines if line and not line.startswith("#")]
    vpn_subnets = [Subnet(subnet) for subnet in list_of_vpns]
    using_vpn = any(args.ip_address in subnet for subnet in vpn_subnets)

    print("{address} {is_or_is_not} using a VPN!".format(
        address=args.ip_address,
        is_or_is_not="is" if using_vpn else "is not",
    ))


if __name__ == "__main__":
    main()
