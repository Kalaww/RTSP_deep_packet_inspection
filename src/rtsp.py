import dpkt

RTSP_PORT = 554

CRLF = "\r\n"

METHOD = [
    "DESCRIBE", "ANNOUNCE", "GET_PARAMETER", "OPTIONS", "PAUSE", "PLAY", "RECORD", "REDIRECT",
    "SETUP", "SET_PARAMETER", "TEARDOWN"
]

GENERAL_HEADERS = [
    "Cache-Control", "Connection", "CSeq", "Date", "Via"
]

REQUEST_HEADERS = [
    "Accept", "Accept-Encoding", "Accept-Language", "Authorization", "Bandwidth", "Blocksize", "Conference",
    "From", "If-Modified-Since", "Proxy-Require", "Range", "Referer", "Require", "Scale", "Session", "Speed",
    "Transport", "User-Agent"
]

RESPONSE_HEADERS = [
    "Allow", "Content-Type", "Public", "Range", "Retry-After", "RTP-Info", "Scale", "Session", "Server", "Speed",
    "Transport", "Unsupported", "WWW-Authenticate"
]

ENTITY_HEADERS = [
    "Content-Base", "Content-Encoding", "Content-Language", "Content-Length", "Content-Location",
    "Content-Type", "Expires", "Last-Modified"
]

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
        self.general_header = {}
        self.request_header = {}
        self.entity_header = {}
        self.others_header = {}

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
            if splitted[0] in REQUEST_HEADERS:
                self.request_header[splitted[0]] = splitted[1]
            elif splitted[0] in ENTITY_HEADERS:
                self.entity_header[splitted[0]] = splitted[1]
            elif splitted[0] in GENERAL_HEADERS:
                self.general_header[splitted[0]] = splitted[1]
            else:
                self.others_header[splitted[0]] = splitted[1]

    def __str__(self):
        str = "## RTSP REQUEST ##\n"
        str += "method: " + self.method + "\n"
        str += "URI: " + self.URI + "\n"
        str += "version: " + self.version + "\n"

        if len(self.general_header) > 0:
            str += "general header:\n"
            for k,v in self.general_header.items():
                str += "\t" + k + ": " + v + "\n"

        if len(self.request_header) > 0:
            str += "request header:\n"
            for k,v in self.request_header.items():
                str += "\t" + k + ": " + v + "\n"

        if len(self.entity_header) > 0:
            str += "entity header:\n"
            for k,v in self.entity_header.items():
                str += "\t" + k + ": " + v + "\n"

        if len(self.others_header) > 0:
            str += "others header:\n"
            for k,v in self.others_header.items():
                str += "\t" + k + ": " + v + "\n"
        return str

class RTSP_Response:

    def __init__(self, raw):
        self.raw = raw
        self.version = None
        self.status_code = None
        self.reason_phrase = None
        self.general_header = {}
        self.response_header = {}
        self.entity_header = {}
        self.others_header = {}

        self.decode()

    def decode(self):
        lines = self.raw.split(CRLF)

        first_line = lines[0].split(" ")
        self.version = first_line[0]
        self.status_code = first_line[1]
        self.reason_phrase = first_line[2]

        for line in lines[1:]:
            splitted = line.split(": ")
            if len(splitted) is not 2:
                continue
            if splitted[0] in RESPONSE_HEADERS:
                self.response_header[splitted[0]] = splitted[1]
            elif splitted[0] in ENTITY_HEADERS:
                self.entity_header[splitted[0]] = splitted[1]
            elif splitted[0] in GENERAL_HEADERS:
                self.general_header[splitted[0]] = splitted[1]
            else:
                self.others_header[splitted[0]] = splitted[1]

    def __str__(self):
        str = "## RTSP RESPONSE ##\n"
        str += "version: " + self.version + "\n"
        str += "status code: " + self.status_code + "\n"
        str += "reason phrase: " + self.reason_phrase + "\n"

        if len(self.general_header) > 0:
            str += "general header:\n"
            for k,v in self.general_header.items():
                str += "\t" + k + ": " + v + "\n"

        if len(self.response_header) > 0:
            str += "response header:\n"
            for k,v in self.response_header.items():
                str += "\t" + k + ": " + v + "\n"

        if len(self.entity_header) > 0:
            str += "entity header:\n"
            for k,v in self.entity_header.items():
                str += "\t" + k + ": " + v + "\n"

        if len(self.others_header) > 0:
            str += "others header:\n"
            for k,v in self.others_header.items():
                str += "\t" + k + ": " + v + "\n"
        return str

class RTSP_Undefined:

    def __init__(self, raw):
        self.raw = raw

    def __str__(self):
        return "## UNDEFINED ##" + "\n"