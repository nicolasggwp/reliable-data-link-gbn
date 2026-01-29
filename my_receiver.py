from frame import Frame
class Receiver:
    """
    Implements the receiver side of a reliable data link layer protocol
    using Go-Back-N ARQ.

    The receiver is responsible for:
    - verifying frame integrity
    - enforcing in-order delivery
    - delivering data to the network layer
    - generating cumulative acknowledgments
    - supporting piggybacking in full-duplex communication
    """
    
    def __init__(self, channel):
        """
        Initialize the receiver state.

        :param channel: Reference to the unreliable Channel
        """

        self.channel = channel
        
        # Sequence number of the next expected DATA frame
        self.expected_seq = 0
        
        # Stores the last acknowledgment number that must be sent
        # Used for cumulative ACKs and piggybacking
        self.ack_pending = None
        
        # Queue simulating data coming from the network layer
        # Used to support piggybacking
        self.network_queue = []
    
    def network_send(self, payload: bytes):
        """
        Simulate data arriving from the network layer.

        This data may later be sent to the sender, possibly with
        a piggybacked acknowledgment.
        """
        self.network_queue.append(payload)

    def send_ack(self):
        """
        Send a standalone ACK frame if an acknowledgment is pending.

        This method is used when there is no outgoing data available
        for piggybacking.
        """

        if self.ack_pending is None:
            return

        ack_num = self.ack_pending
        
        # Create an ACK-only frame
        ack_frame = Frame(frame_type=1, seq=0, ack=ack_num, payload=b"")
        
        
        raw = ack_frame.to_bytes_all()
        
        # Send ACK frame to sender
        self.channel.send(raw, direction="receiver_to_sender")
        
        print(f"Receiver: sent standalone ACK={self.ack_pending}")
        
        # Clear pending ACK after transmission
        self.ack_pending = None 
    
    def send_data(self, payload: bytes):
        """
        Send a DATA frame from the receiver to the sender.

        If an acknowledgment is pending, it is piggybacked
        in the ACK field of the DATA frame.
        """

        ack = self.ack_pending if self.ack_pending is not None else 0
        
        # Create DATA frame with piggybacked ACK
        frame = Frame(frame_type=0, seq=0, ack=ack, payload=payload)
        
        raw = frame.to_bytes_all()
        
        # Send DATA frame to sender
        self.channel.send(raw, direction="receiver_to_sender")
        
        print(f"Receiver: sent data with piggybacking ACk={ack}")
        
        # ACK has been sent, clear pending ACK
        self.ack_pending = None

    def receive(self, raw: bytes):
        """
        Handle an incoming frame from the sender.

        This method:
        - verifies frame integrity
        - checks sequence number ordering
        - delivers valid data to the network layer
        - updates cumulative ACK state
        - sends ACKs (standalone or piggybacked)
        """

        try:
            frame = Frame.from_bytes(raw)
        except ValueError:
            # Corrupted frame: discard and acknowledge last correct frame
            print("Receiver: corrupted frame discarted")
            self.send_ack()
            return
        
        # Check if frame is the expected one
        if frame.seq == self.expected_seq:
            print(f"Receiver: received expected frame seq={frame.seq}")
            
            # Deliver payload to network layer
            self.deliver_to_network(frame.payload)
            
            # Advance expected sequence number (modulo 8)
            self.expected_seq = (self.expected_seq + 1) % 8
        else:
            # Out-of-order frame: discard
            print(f"Receiver: out-of-order frame seq={frame.seq}, expected={self.expected_seq}")
        
        # Update cumulative ACK number
        self.ack_pending = (self.expected_seq - 1) % 8
        
        # If there is data to send, piggyback the ACK
        if self.network_queue:
            payload = self.network_queue.pop(0)
            self.send_data(payload)
        else:
            # Otherwise, send a standalone ACK
            self.send_ack()
    
    def deliver_to_network(self, payload: bytes):
        """
        Deliver correctly received data to the (simulated) network layer.
        """

        print(f"Receiver: delivered to network -> {payload}")



