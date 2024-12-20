import argparse

from .dashboard.app import run_dashboard
from .network_interface.app import scan_for_network_interfaces
from .output_pcat.app import output_pcap


def main():
    parser = argparse.ArgumentParser(description="MyrMyr CLI")
    subparser = parser.add_subparsers(dest="command", required=True)

    parser1 = subparser.add_parser("dashboard", help="Dashboard command")
    parser1.add_argument("--interface", required=True, help="Interface to sniff")

    subparser.add_parser("interface", help="Interface command")

    parser3 = subparser.add_parser("output", help="Interface command")
    parser3.add_argument("--interface", required=True, help="Interface to sniff")
    parser3.add_argument(
        "--filename", default="capture_output.pcap", help="Output file"
    )
    parser3.add_argument("--count", default=10, help="Number of packets to capture")

    args = parser.parse_args()

    if args.command == "dashboard":
        run_dashboard(args.interface)

    elif args.command == "interface":
        scan_for_network_interfaces()

    elif args.command == "output":
        output_pcap(args.interface, args.count, args.filename)
