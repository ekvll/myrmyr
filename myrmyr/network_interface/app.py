import psutil


def scan_for_network_interfaces() -> None:
    """Scan network interfaces and print details.

    Examples
    --------
    >>> scan_network_interfaces()
    Interface: ...
    """

    interfaces = psutil.net_if_addrs()
    for interface, addresses in interfaces.items():
        print(f"Interface: {interface}")
        for address in addresses:
            print(
                f"  Address: {address.address} | Family: {address.family} | Netmask: {address.netmask}"
            )
        print()  # Add a newline for better readability
