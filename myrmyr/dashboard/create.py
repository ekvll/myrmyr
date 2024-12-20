import threading
from collections import defaultdict

import dash
import pandas as pd
import plotly.express as px
from dash import callback_context, dash_table, dcc, html
from dash.dependencies import Input, Output, State
from ipwhois import IPWhois

from .utils import sort_dict_by_value

packet_df = pd.DataFrame(
    columns=["src_ip", "dst_ip", "protocol", "length", "time", "src_port", "dst_port"]
)
lock = threading.Lock()
max_packet_lengths = defaultdict(int)
port_usage = defaultdict(int)


def extract_packet_features(packet) -> list | None:
    """Extract information, or features, from a single packet.

    Parameters
    ----------
    packet : _type_
        Packet to extract features from.

    Returns
    -------
    list | None
        A list of features, if features exists. Else returns None.
    """
    try:
        src_ip = packet.ip.src if hasattr(packet, "ip") else None
        dst_ip = packet.ip.dst if hasattr(packet, "ip") else None
        protocol = (
            packet.transport_layer if hasattr(packet, "transport_layer") else None
        )
        length = int(packet.length) if hasattr(packet, "length") else None
        timestamp = packet.sniff_time

        src_port = getattr(packet[protocol], "srcport", None) if protocol else None
        dst_port = getattr(packet[protocol], "dstport", None) if protocol else None

        return [src_ip, dst_ip, protocol, length, timestamp, src_port, dst_port]

    except AttributeError:
        # Ignore packets without the required attributes
        return None


def update_packet_df(capture) -> None:
    """Updates the Pandas DataFrame that is visualized in the web application with new rows of data.

    Parameters
    ----------
    capture : _type_
        The capture object from which packets are fetched.

    Returns
    -------
    None
    """
    global packet_df, lock, max_packet_lengths, port_usage
    for packet in capture.sniff_continuously():
        features = extract_packet_features(packet)
        if features:
            with lock:
                packet_df.loc[len(packet_df)] = features

                # Update maximum packet length for the protocol
                protocol = features[2]
                length = features[3]
                if length > max_packet_lengths[protocol]:
                    max_packet_lengths[protocol] = length

                # Update port usage counts
                src_port = features[5]
                dst_port = features[6]
                if src_port:
                    port_usage[int(src_port)] += 1
                if dst_port:
                    port_usage[int(dst_port)] += 1


def port_usage_table():
    return dash_table.DataTable(
        id="port-usage-table",
        columns=[
            {"name": "Port Number", "id": "port", "type": "numeric"},
            {"name": "Usage Count", "id": "usage_count", "type": "numeric"},
        ],
        data=[],  # Start with empty data
        style_table={
            "maxHeight": "300px",  # Adjust height to show 10 rows (approx)
            "overflowY": "auto",  # Enable vertical scrolling
            "overflowX": "auto",  # Enable horizontal scrolling if needed
        },
        style_cell={
            "textAlign": "left",
            "whiteSpace": "normal",  # Prevent text clipping
            "height": "auto",  # Auto-adjust row height for wrapped text
        },
        # page_size=10,  # Show 10 rows per page
        sort_action="native",  # Enable built-in sorting
        sort_mode="single",  # Allow sorting by one column at a time; use "multi" for multi-column sorting
    )


def ip_pair_table():
    return dash_table.DataTable(
        id="ip-pair-table",
        columns=[
            {
                "name": "Source -> Destination IP Pair",
                "id": "ip_pair",
            },  # Use the combined column 'ip_pair'
            {"name": "Usage Count", "id": "count"},
        ],
        data=[],  # Start with empty data
        style_table={
            "maxHeight": "300px",  # Adjust height to show 10 rows (approx)
            "overflowY": "auto",  # Enable vertical scrolling
            "overflowX": "auto",  # Enable horizontal scrolling if needed
        },
        style_cell={
            "textAlign": "left",
            "whiteSpace": "normal",  # Prevent text clipping
            "height": "auto",  # Auto-adjust row height for wrapped text
        },
        sort_action="native",  # Enable built-in sorting
        sort_mode="single",  # Allow sorting by one column at a time
    )


def create_dashboard(df_tail: int = 2000) -> dash.Dash:
    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            html.H1("Real-Time Network Traffic Monitoring"),
            dcc.Graph(id="live-traffic-graph"),
            dcc.Graph(id="max-packet-length-graph"),
            port_usage_table(),
            html.Div(style={"marginBottom": "30px"}),
            html.H1("IP Whois Lookup", style={"textAlign": "center"}),
            dcc.Input(
                id="ip-input",
                type="text",
                placeholder="Enter IP Address",
                style={"width": "50%", "margin-bottom": "10px"},
            ),
            html.Div(
                [
                    html.Button(
                        "Lookup",
                        id="lookup-button",
                        n_clicks=0,
                        style={"margin-right": "10px"},
                    ),
                    html.Button("Clear", id="clear-button", n_clicks=0),
                ]
            ),
            html.Div(
                id="whois-result",
                style={"margin-top": "20px", "whiteSpace": "pre-wrap"},
            ),
            ip_pair_table(),
            # Interval component for updating the graph every two seconds
            dcc.Interval(
                id="interval-component",
                interval=2 * 1000,  # 1000 milliseconds = 1 second
                n_intervals=0,  # Start at 0
            ),
        ]
    )

    # Callback to update the graph every two seconds
    @app.callback(
        Output("live-traffic-graph", "figure"),
        [Input("interval-component", "n_intervals")],
    )
    def update_graph(n):
        global packet_df, lock

        with lock:  # Ensure thread-safe access to packet_df
            if packet_df.empty:
                return px.line(title="No data yet")

        # Ensure 'time' is properly formatted as datetime
        packet_df = packet_df.dropna(subset=["time"])  # Drop rows with invalid time

        # Plot: Packet length over time
        fig = px.line(
            packet_df.tail(df_tail),  # Display the last 'tail' rows of the DataFrame
            x="time",
            y="length",
            color="protocol",  # Color lines by protocol (e.g., TCP, UDP)
            title="Network Traffic Over Time",
            labels={"length": "Packet Length (Bytes)", "time": "Timestamp"},
        )

        return fig

    @app.callback(
        Output("max-packet-length-graph", "figure"),
        [Input("interval-component", "n_intervals")],
    )
    def update_max_packet_length_graph(n):
        # Create a histogram of maximum packet lengths by protocol
        protocols = list(max_packet_lengths.keys())
        max_lengths = list(max_packet_lengths.values())

        fig = px.bar(
            x=protocols,
            y=max_lengths,
            title="Maximum Packet Length by Protocol",
            labels={"x": "Protocol", "y": "Max Packet Length (Bytes)"},
        )

        return fig

    @app.callback(
        Output("port-usage-table", "data"), [Input("interval-component", "n_intervals")]
    )
    def update_port_usage_table(n):
        sorted_port_usage = sort_dict_by_value(port_usage)

        # Convert the port_usage dictionary to a list of dictionaries for the table
        return [
            {"port": port, "usage_count": count}
            for port, count in sorted_port_usage.items()
        ]

    @app.callback(
        Output("ip-pair-table", "data"), [Input("interval-component", "n_intervals")]
    )
    def update_ip_pair_table(n):
        unique_ip_pairs = (
            packet_df.groupby(["src_ip", "dst_ip"]).size().reset_index(name="count")
        )
        unique_ip_pairs["ip_pair"] = (
            unique_ip_pairs["src_ip"] + " -> " + unique_ip_pairs["dst_ip"]
        )

        unique_ip_pairs = unique_ip_pairs.sort_values(by="count", ascending=False)
        return unique_ip_pairs.to_dict("records")

    # Callback to perform the IP Whois lookup

    @app.callback(
        [Output("ip-input", "value"), Output("whois-result", "children")],
        [Input("lookup-button", "n_clicks"), Input("clear-button", "n_clicks")],
        State("ip-input", "value"),
    )
    def handle_buttons(lookup_clicks, clear_clicks, ip):
        # Determine which button was clicked
        ctx = callback_context
        if not ctx.triggered:
            return (
                dash.no_update,
                "",
            )  # Optional add string within second pair of "" to display message

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if triggered_id == "lookup-button" and ip:  # Lookup functionality
            try:
                obj = IPWhois(ip)
                results = obj.lookup_rdap()
                formatted_result = "\n".join(
                    [f"{key}: {value}" for key, value in results.items()]
                )
                return dash.no_update, f"Whois Result for {ip}:\n\n{formatted_result}"
            except Exception as e:
                return dash.no_update, f"Error: {str(e)}"

        elif triggered_id == "clear-button":  # Clear functionality
            return (
                "",
                "",
            )  # Optional add string within second pair of "" to display message

        return dash.no_update, dash.no_update

    return app
