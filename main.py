from my_channel import Channel
from my_sender import Sender
from my_receiver import Receiver
import time


# Create an unreliable channel simulation
# loss_prob: probability that a frame is lost
# corrupt_prob: probability that a frame is corrupted
channel = Channel(loss_prob=0.1, corrupt_prob=0.2)

# Create sender and receiver entities
# Both share the same channel instance
sender = Sender(channel)
receiver = Receiver(channel)

# Connect sender and receiver through the channel
# This allows bidirectional communication
channel.connect(sender, receiver)

# Data coming from receiver's network layer (for piggybacking)
receiver.network_send(b"reply-1")
receiver.network_send(b"reply-2")
receiver.network_send(b"reply-3")
receiver.network_send(b"reply-4")

# Data coming from sender's network layer
sender.send_data(b"msg-1")
sender.send_data(b"msg-2")
sender.send_data(b"msg-3")
sender.send_data(b"msg-4")
sender.send_data(b"msg-5")
sender.send_data(b"msg-6")
sender.send_data(b"msg-7")
sender.send_data(b"msg-8")
sender.send_data(b"msg-9")

# Main simulation loop
# Periodically checks for sender timeouts
# Retransmissions are triggered if ACKs are not received in time
while True:
    sender.check_timeout()
    time.sleep(0.1)
