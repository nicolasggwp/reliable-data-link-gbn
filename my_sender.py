import time
from frame import Frame
class Sender:
    """
    Implements the sender side of a reliable data link layer protocol
    using a Go-Back-N sliding window.

    The sender is responsible for:
    - framing data from the network layer
    - assigning sequence numbers
    - transmitting frames
    - handling cumulative acknowledgments
    - managing timeouts and retransmissions
    - handling piggybacked data from the receiver
    """
    
    def __init__(self, channel):
        """
        Initialize the sender state.

        :param channel: Reference to the unreliable Channel
        """
        
        self.channel = channel
        
        # Maximum number of outstanding (unacknowledged) frames
        self.window_size = 7
        
        # Sequence number of the oldest unacknowledged frame
        self.base = 0
        
        # Sequence number to be assigned to the next outgoing frame
        self.next_seq = 0
        
        #Max seq
        self.MAX_SEQ = 8

        # Buffer of sent but not yet acknowledged frames
        # Key: absolute sequence number
        # Value: Frame object
        self.buffer = {}
        
        # Timer for the oldest unacknowledged frame
        self.timer_start = None
        
        # Timeout duration in seconds
        self.timeout = 2.0

    def send_data(self, payload: bytes):
        """
        Send data from the (simulated) network layer.

        This method:
        - checks if the send window has space
        - creates a DATA frame
        - sends it through the channel
        - stores it in the retransmission buffer
        """
        
        # Check if the sliding window is full
        if self.next_seq >= self.base + self.window_size:
            print("Sender window full, cannot send now")
            return
        
        # Create a DATA frame
        frame = Frame(frame_type=0, seq=self.next_seq % 8, ack=0, payload=payload)
        
        # Serialize frame into raw bytes
        raw = frame.to_bytes_all()
        
        # Send frame through the channel
        self.channel.send(raw, direction="sender_to_receiver")
        
        # Store frame in buffer for possible retransmission
        self.buffer[self.next_seq] = frame
        
        print(f"Sender: sent frame seq={self.next_seq}")
        
        # Advance next sequence number
        self.next_seq += 1
        
        # Start timer if this is the first unacknowledged frame
        if self.base == self.next_seq:
            self.timer_start = time.time()

    def receive_ack(self, raw: bytes):
        """
        Handle incoming frames from the receiver.

        This method processes:
        - standalone ACK frames
        - piggybacked DATA + ACK frames
        """
        
        # Attempt to decode and verify the received frame
        try:
            frame = Frame.from_bytes(raw)
        except ValueError:
            print("Sender: received corrupted ACK")
            return
        
        # If the frame contains DATA (piggybacking case),
        # deliver it to the network layer
        if frame.frame_type == 0:
            print(f"Sender: received DATA from receiver -> {frame.payload}")
            self.deliver_to_network(frame.payload)

        # Extract cumulative acknowledgment number
        ack = frame.ack
        

        # Slide the window if the ACK is valid
        new_base = self.base
        while new_base < self.next_seq:
            if new_base % self.MAX_SEQ == ack:
                self.base = new_base + 1
                print(f"Sender: ACK received, base updated to {self.base}")
                break
            new_base += 1
            
        # Remove acknowledged frames from buffer
        keys_to_remove = [k for k in self.buffer if k < self.base]
        for k in keys_to_remove:
            del self.buffer[k]
        
        # Timer management
        if not self.buffer:
            # No outstanding frames -> stop timer
            self.timer_start = None
        else:
            # Outstanding frames remain -> restart timer
            self.timer_start = time.time()
    
    def check_timeout(self):
        """
        Check if the retransmission timer has expired.

        If a timeout occurs:
        - all frames currently in the window are retransmitted
        - follows Go-Back-N retransmission strategy
        """

        if self.timer_start is None:
            return
        

        if time.time() - self.timer_start >= self.timeout:
            print("Sender: TIMEOUT, retransmitting window")
            
            # Restart timer
            self.timer_start = time.time()

            # Retransmit all outstanding frames (go-back-n)
            seq = self.base
            while seq < self.next_seq:
                frame = self.buffer.get(seq)
                if frame is not None:
                    raw = frame.to_bytes_all()
                    self.channel.send(raw, direction="sender_to_receiver")
                    print(f"Sender: retransmitted frame seq={seq}")
                seq += 1 

    def deliver_to_network(self, payload: bytes):
        """
        Deliver received data to the (simulated) network layer.
        """
        print(f"Sender: delivered to network -> {payload}")
