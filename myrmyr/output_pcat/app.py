import os

import pyshark

path_pcap_dir = "./data/pcap/"
os.makedirs(path_pcap_dir, exist_ok=True)


def output_pcap(network_interface, packet_count, output_filename):
    global path_pcap_dir

    if not isinstance(packet_count, int):
        packet_count = int(packet_count)

    if not output_filename.endswith(".pcap"):
        output_filename += ".pcap"

    output_filepath = os.path.join(path_pcap_dir, output_filename)

    capture = pyshark.LiveCapture(
        interface=network_interface,
        output_file=output_filepath,
    )

    print(f"Capturing {packet_count} packets on interface {network_interface}")

    capture.sniff(packet_count=packet_count)

    print(f"Capture complete. Saved {packet_count} packets to {output_filepath}")
