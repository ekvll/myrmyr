## myrmyr

**myrmyr** is a network traffic analyzer and visualizer that allows you to monitor and capture network packets in real-time, providing an intuitive dashboard and the ability to save packets for offline analysis.

---

### Features

* **Real-time traffic monitoring**: View ongoing network traffic via a web-based dashboard. Additionally, functionality to perform IP lookups inside the dashboard.
* **Scan for active network interfaces**: Scan your computer for active network interfaces.
* **Packet sniffing and storage**: Capture a specified number of packets from a given network interface and save them to a PCAP file for offline analysis.

---

### Installation

Navigate to the desired directory:
```bash
cd /path/to/your/directory
```

Clone the repository
```bash
git clone https://github.com/ekvll/myrmyr.git
```

Access the cloned repository:
```bash
cd myrmyr/
```

Install **myrmyr**:
```bash
python -m pip install -e .
```

---

### Usage

First, make sure that you have **myrmyr** installed:
```bash
myrmyr --version
```

#### Scan for Available Network Interfaces

To scan for available network interfaces:
```bash
myrmyr scan
```
#### Dashboard Web Application

To run the dashboard web application:
```bash
myrmyr dashboard --interface <interface>
```
where
* ```<interface>``` is the network interface to monitor.

#### Save Network Traffic to a File

To save a given number of network traffic packets to a PCAP file:
```bash
myrmyr output --interface <interface> --count <n_packets> --filename <filename>
```
where:
* ```<interface>``` is the network interface to listen to.
* ```<n_packets>``` is the number of packets to save. Default is 10.
* ```<filename>``` is the output filename. Default is 'capture_output.pcap'.

Output files are stored in the directory ```/data/pcap/```, which is automatically created if it does not already exist.

---

### Disclaimer

This project is intended solely for educational purposes to demonstrate and learn about network analysis and traffic inspection techniques. Unauthorized network sniffing or monitoring is strictly prohibited and may violate privacy laws, organizational policies, or terms of service agreements.

Users are responsible for ensuring their use of this software complies with applicable laws and regulations. The authors and contributors of this repository do not condone or take responsibility for any misuse or unethical application of this tool. Always obtain proper authorization before analyzing or capturing network traffic.

---

### License

**myrmyr** is licensed under the [MIT license](LICENSE).