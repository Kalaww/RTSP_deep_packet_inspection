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

def decode_type(packet):
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
        return None


class RTSP_Packets_Hanlder:

    def __init__(self, packets):
        self.raw_packets = packets
        self.packets = []
        self.decode_all()

    def decode_all(self):
        current = None
        for packet in self.raw_packets:
            if len(packet.data) == 0 or len(packet.data.data) == 0 or len(packet.data.data.data) == 0:
                continue
            if packet.data.data.dport == RTSP_PORT or packet.data.data.sport == RTSP_PORT:
                if current is None:
                    current = decode_type(packet)
                    if current is not None and current.decode():
                        self.packets.append(current)
                        current = None
                else:
                    if current.more(packet.data.data.data):
                        self.packets.append(current)
                        current = None


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
        self.content = ''
        self.nb_packets = 1

    def decode(self):
        lines = self.raw.split(CRLF)

        first_line = lines.pop(0).split(" ")
        self.method = first_line[0]
        self.URI = first_line[1]
        self.version = first_line[2]

        while len(lines) > 0:
            line = lines.pop(0)
            splitted = line.split(": ")
            if len(line) == 0 and len(lines) > 0 and "Content-Length" in self.entity_header:
                self.content = ''.join(lines)
                if len(self.content) < int(self.entity_header["Content-Length"]):
                    return False
                else:
                    return True
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
        return True

    def more(self, content):
        self.content = self.content.join(content)
        self.nb_packets += 1
        if len(self.content) < int(self.entity_header["Content-Length"]):
            return False
        return True

    def __str__(self):
        s = "## RTSP REQUEST ## (nb packet: " + str(self.nb_packets) +")\n"
        s += "method: " + self.method + "\n"
        s += "URI: " + self.URI + "\n"
        s += "version: " + self.version + "\n"

        if len(self.general_header) > 0:
            s += "general header:\n"
            for k,v in self.general_header.items():
                s += "\t" + k + ": " + v + "\n"

        if len(self.request_header) > 0:
            s += "request header:\n"
            for k,v in self.request_header.items():
                s += "\t" + k + ": " + v + "\n"

        if len(self.entity_header) > 0:
            s += "entity header:\n"
            for k,v in self.entity_header.items():
                s += "\t" + k + ": " + v + "\n"

        if len(self.others_header) > 0:
            s += "others header:\n"
            for k,v in self.others_header.items():
                s += "\t" + k + ": " + v + "\n"

        if len(self.content) > 0:
            s += "content:\n" + self.content + "\n"
        return s

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
        self.content = ''
        self.nb_packets = 1

    def decode(self):
        lines = self.raw.split(CRLF)

        first_line = lines.pop(0).split(" ")
        self.version = first_line[0]
        self.status_code = first_line[1]
        self.reason_phrase = first_line[2]

        while len(lines) > 0:
            line = lines.pop(0)
            splitted = line.split(": ")
            if len(line) == 0 and len(lines) > 0 and "Content-Length" in self.entity_header:
                self.content = CRLF.join(lines)
                if len(self.content) < int(self.entity_header["Content-Length"]):
                    return False
                else:
                    return True
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
        return True

    def more(self, content):
        self.content += content
        self.nb_packets += 1
        if len(self.content) < int(self.entity_header["Content-Length"]):
            return False
        return True

    def __str__(self):
        s = "## RTSP RESPONSE ## (nb packet: " + str(self.nb_packets) +")\n"
        s += "version: " + self.version + "\n"
        s += "status code: " + self.status_code + "\n"
        s += "reason phrase: " + self.reason_phrase + "\n"

        if len(self.general_header) > 0:
            s += "general header:\n"
            for k,v in self.general_header.items():
                s += "\t" + k + ": " + v + "\n"

        if len(self.response_header) > 0:
            s += "response header:\n"
            for k,v in self.response_header.items():
                s += "\t" + k + ": " + v + "\n"

        if len(self.entity_header) > 0:
            s += "entity header:\n"
            for k,v in self.entity_header.items():
                s += "\t" + k + ": " + v + "\n"

        if len(self.others_header) > 0:
            s += "others header:\n"
            for k,v in self.others_header.items():
                s += "\t" + k + ": " + v + "\n"

        if len(self.content) > 0:
            s += "content:\n" + self.content + "\n"
        return s

class RTSP_Undefined:

    def __init__(self, raw):
        self.raw = raw

    def __str__(self):
        return "## UNDEFINED ##" + "\n"