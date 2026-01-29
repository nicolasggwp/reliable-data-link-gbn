# Frame type identifiers
DATA = 0
ACK = 1

class Frame:
    """
    Represents a data link layer frame used by the Go-Back-N protocol.

    Each frame contains:
    - a compact 1-byte header (type, sequence number, acknowledgment number)
    - a payload of variable length
    - a simple checksum for error detection
    """

    def __init__(self, frame_type, seq, ack, payload: bytes):
        """
        Create a new frame.

        :param frame_type: DATA (0) or ACK (1)
        :param seq: Sequence number (0–7)
        :param ack: Cumulative acknowledgment number (0–7)
        :param payload: Payload as raw bytes
        """
        
        # Validate frame type
        if frame_type not in (DATA, ACK):
            raise ValueError("Frame type must be DATA (0) or ACK (1)")
        
        # Validate sequence number (3 bits)
        if not (0 <= seq <= 7):
            raise ValueError("Invalid sequence number (must be 0-7)")
        
        # Validate acknowledgment number (3 bits)
        if not (0 <= ack <= 7):
            raise ValueError("ACK number must be between 0 and 7")
        
        # Validate payload
        if not isinstance(payload, bytes):
            raise ValueError("Payload must be bytes")
        
        # Maximum payload length is 255 bytes (1 byte length field)
        if len(payload) > 255:
            raise ValueError("Payload too large (max 255 bytes)")
        
        # Assign fields
        self.frame_type = frame_type
        self.seq = seq
        self.ack = ack
        self.payload = payload
        self.length = len(payload)
        
        # Checksum is computed during serialization
        self.checksum = None
    
    def build_header(self):
        """
        Build the 1-byte frame header.

        Header format (bit-level):
        - bits 7–6: frame type (DATA or ACK)
        - bits 5–3: sequence number
        - bits 2–0: acknowledgment number
        """
        
        header = 0
        header |= (self.frame_type & 0b11) << 6
        header |= (self.seq & 0b111) << 3
        header |= (self.ack & 0b111)
        return header
    
    def to_bytes_without_checksum(self) -> bytes:
        """
        Serialize the frame into bytes without the checksum.

        Layout:
        [ Header (1 byte) | Length (1 byte) | Payload (N bytes) ]
        """

        header = self.build_header().to_bytes(1, "big")
        length = self.length.to_bytes(1, "big")
        payload = self.payload
        return header + length + payload
    
    @staticmethod
    def calculate_checksum(data: bytes) -> int:
        """
        Compute a simple checksum over the given data.

        The checksum is the sum of all bytes modulo 256.
        """

        return sum(data) % 256
    
    def to_bytes_all(self) -> bytes:
        """
        Serialize the complete frame into bytes, including the checksum.

        Layout:
        [ Header | Length | Payload | Checksum ]
        """

        data = self.to_bytes_without_checksum()
        checksum = Frame.calculate_checksum(data).to_bytes(1, "big")
        return data + checksum
    
    @staticmethod
    def from_bytes(raw: bytes):
        """
        Deserialize raw bytes into a Frame object.

        Performs:
        - minimum length validation
        - length field validation
        - checksum verification
        - header field extraction
        """
        
        # Minimum frame size: header + length + checksum
        if len(raw) < 3:
            raise ValueError("Frame too short")
        
        # Extract fixed fields
        header = raw[0]
        length = raw[1]
        
        # Expected total size based on length field
        expected_size = 1 + 1 + length + 1
        
        # Validate frame length
        if len(raw) != expected_size:
            raise ValueError("Invalid frame length")
        
        # Extract payload and checksum
        payload = raw[2:2 + length]
        received_checksum = raw[-1]
        
        # Recalculate checksum
        data_without_checksum = raw[:-1]
        calculated = Frame.calculate_checksum(data_without_checksum)
        
        if calculated != received_checksum:
            raise ValueError("Checksum mismatch")
        
        # Decode header fields
        frame_type = (header >> 6) & 0b11
        seq = (header >> 3) & 0b111
        ack = header & 0b111
        
        return Frame(frame_type, seq, ack, payload)









