import dpkt

RTSP_PORT = 554

CRLF = "\r\n"

TYPE_REQUEST = "REQUEST"
TYPE_RESPONSE = "RESPONSE"
TYPE_UNKNOWN = "UNKNOWN"

METHOD = {
    "DESCRIBE", "ANNOUNCE", "GET_PARAMETER", "OPTIONS", "PAUSE", "PLAY", "RECORD", "REDIRECT",
    "SETUP", "SET_PARAMETER", "TEARDOWN"
}

def get_RTSP_packets(packets):
    rtsp = []

    for packet in packets:
        if len(packet.data) == 0:
            continue
        internet_layer = packet.data
        if len(internet_layer.data) == 0:
            continue
        transport_layer = internet_layer.data
        if len(transport_layer.data) == 0:
            continue
        if transport_layer.dport == RTSP_PORT or transport_layer.sport == RTSP_PORT:
            rtsp.append(decode(packet))
    return rtsp

def decode(packet):
    content = packet.data.data.data
    if len(content) == 0:
        return None
    else:
        lines = content.split(CRLF)
        first_line = lines[0].split(" ")
        if first_line[0] in METHOD:
            return RTSP_Request(content)
        elif first_line[0].startswith("RTSP"):
            return RTSP_Response(content)
        return RTSP_Undefined(content)

class RTSP_Request:

    def __init__(self, raw):
        self.raw = raw
        self.method = None
        self.URI = None
        self.version = None
        self.header = {}
        self.decode()

    def decode(self):
        lines = self.raw.split(CRLF)

        first_line = lines[0].split(" ")
        self.method = first_line[0]
        self.URI = first_line[1]
        self.version = first_line[2]

        for line in lines[1:]:
            splitted = line.split(": ")
            if len(splitted) is not 2:
                continue
            self.header[splitted[0]] = splitted[1]

    def __str__(self):
        str = "RTSP REQUEST\n"
        str += "method: " + self.method + "\n"
        str += "URI: " + self.URI + "\n"
        str += "version: " + self.version + "\n"

        if len(self.header) > 0:
            str += "header:\n"
            for k,v in self.header.items():
                str += "\t" + k + ": " + v + "\n"
        return str

class RTSP_Response:

    def __init__(self, raw):
        self.raw = raw
        self.version = None
        self.status_code = None
        self.reason_phrase = None
        self.decode()

    def decode(self):
        lines = self.raw.split(CRLF)

        first_line = lines[0].split(" ")
        self.version = first_line[0]
        self.status_code = first_line[1]
        self.reason_phrase = first_line[2]

    def __str__(self):
        str = "RTSP RESPONSE\n"
        str += "version: " + self.version + "\n"
        str += "status code: " + self.status_code + "\n"
        str += "reason phrase: " + self.reason_phrase + "\n"
        return str

class RTSP_Undefined:

    def __init__(self, raw):
        self.raw = raw

    def __str__(self):
        return "UNDEFINED" + "\n"