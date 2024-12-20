import threading

import pyshark

from .create import create_dashboard, update_packet_df


def run_dashboard(network_interface):
    capture = pyshark.LiveCapture(interface=network_interface)

    packet_thread = threading.Thread(target=update_packet_df, args=(capture,))
    packet_thread.daemon = True
    packet_thread.start()

    app = create_dashboard()
    app.run_server(debug=True)
