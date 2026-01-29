import random
class Channel:
    """
    Simulates an unreliable point-to-point communication channel.

    This class represents the physical/data link medium between Sender and Receiver.
    It can randomly:
    - lose frames
    - corrupt frames

    The channel is bidirectional and does not buffer frames.
    """
    
    def __init__(self, loss_prob=0.4, corrupt_prob=0.2):
        """
        Initialize the channel with configurable error probabilities.

        :param loss_prob: Probability that a frame is lost (not delivered)
        :param corrupt_prob: Probability that a frame is corrupted (bit-flipped)
        """
        self.loss_prob = loss_prob
        self.corrupt_prob = corrupt_prob
        
        # References to protocol endpoints (set later via connect)
        self.sender = None
        self.receiver = None
    
    def connect(self, sender, receiver):
        """
        Connect the channel to a Sender and a Receiver.

        This simulates plugging both endpoints into the same link.
        """
        self.sender = sender
        self.receiver = receiver

    def send(self, data: bytes, direction="sender_to_receiver"):
        """
        Transmit a frame through the channel.

        The frame may be:
        - lost
        - corrupted
        - delivered correctly

        :param data: Raw frame bytes
        :param direction: Transmission direction
                          ("sender_to_receiver" or "receiver_to_sender")
        """
        
        # Simulate random frame loss
        if random.random() < self.loss_prob:
            print("Channel: frame lost")
            return
        
        raw = data
        
        # Simulate random frame corruption
        if random.random() < self.corrupt_prob:
            raw = self.corrupt(raw)
            print("Channel: frame corrupted")
        
        # Deliver the frame to the appropriate endpoint
        if direction == "sender_to_receiver":
            # Data or ACK going to the receiver
            self.receiver.receive(raw)
        else:
            # ACK or piggybacked data going back to the sender
            self.sender.receive_ack(raw)

    def corrupt(self, raw: bytes) -> bytes:
        """
        Corrupt a frame by flipping a random byte.

        This simulates bit errors on the link.
        """
        
        # Empty frames cannot be corrupted
        if len(raw) == 0:
            return raw
        
        # Convert to mutable bytearray
        b = bytearray(raw)
        
        # Choose a random byte to corrupt
        index = random.randint(0, len(b) - 1)
        
        # Flip all bits in the selected byte
        b[index] ^= 0xFF
        
        return bytes(b)
