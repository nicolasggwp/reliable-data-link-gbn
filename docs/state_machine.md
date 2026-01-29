# State Machine – Reliable Data Link Protocol (Go-Back-N)

This section describes the complete state machines for the Sender, Receiver, and Unreliable Channel used in this project.

The model is event-driven, and most states are logical states derived from protocol variables rather than explicit state flags in the code.

## Sender State Machine

The sender can be modeled using two logical states, derived from the relationship between the sliding window variables.

### Sender States

#### State: IDLE

Description
- The sender has no outstanding (unacknowledged) frames.

Logical conditions
- base == next_seq
- Retransmission buffer is empty
- Timer is stopped (timer_start == None)

Meaning
- No frames are in flight
- No timeout can occur
- Sender is waiting for data from the network layer

#### State: ACTIVE

Description
- The sender has one or more unacknowledged frames in flight.

Logical conditions
- base < next_seq
- Retransmission buffer contains at least one frame
- Timer is running (timer_start != None)

Meaning
- Frames are outstanding
- Cumulative ACKs are expected
- Timeout and retransmissions are possible

### Sender Transitions

#### IDLE → ACTIVE

Event
- Network layer provides data
- Send window is not full

Actions
- Create a DATA frame
- Assign a sequence number
- Send the frame through the channel
- Store the frame in the retransmission buffer
- Start the timer
- Increment next_seq

#### ACTIVE → ACTIVE (Continuous Send)

Event
- Network layer provides new data
- Send window still has available space

Actions
- Create and send a new DATA frame
- Store it in the buffer
- Increment next_seq
- Timer remains unchanged

#### ACTIVE → ACTIVE (Partial ACK)

Event
- Reception of a cumulative ACK
- At least one unacknowledged frame remains

Actions
- Advance base according to the ACK
- Remove acknowledged frames from the buffer
- Restart the timer

#### ACTIVE → IDLE

Event
- Reception of a cumulative ACK
- All outstanding frames are acknowledged

Condition
- Retransmission buffer becomes empty

Actions
- Stop the timer

#### ACTIVE → ACTIVE (Timeout)

Event
- Timer expiration

Actions
- Retransmit all frames in the interval [base, next_seq)
- Restart the timer

Note
This behavior strictly follows the Go-Back-N ARQ retransmission strategy.

## Receiver State Machine (Simplified)

The receiver is intentionally simple and is modeled with a single persistent state.

### Receiver State

#### State: WAIT

Description
- The receiver is always waiting for the next incoming frame.

State variable
- expected_seq

### Receiver Behavior (Event-driven)

#### Event: Frame received
Case 1 — Correct frame

Conditions
- Checksum is valid
- seq == expected_seq

Actions
- Deliver payload to the network layer
- Increment expected_seq
- Update cumulative ACK number

Case 2 — Incorrect frame

Conditions
- Frame is corrupted, or
- Frame is out of order (seq != expected_seq)

Actions
- Discard the frame
- Keep expected_seq unchanged
- Prepare ACK for the last correctly received frame

### Acknowledgment Transmission (Immediate Action)

After processing any received frame, the receiver always sends an acknowledgment:

If there is data to send to the sender:
- Send a DATA frame with a piggybacked ACK

Otherwise:
- Send a standalone ACK frame

After sending the ACK, the receiver remains in state WAIT.

### Design Note

ACK transmission is modeled as an action, not as a state, because it does not represent a persistent protocol condition.

## Unreliable Channel State Machine

The channel is modeled as a stateless, memoryless component.

### Channel Behavior

#### Event: send(frame)

For each transmitted frame, the channel randomly selects one of the following outcomes:

Deliver
- Frame is delivered correctly to the destination

Corrupt
- One or more bits of the frame are modified

Drop
- Frame is lost and never delivered

The probabilities of corruption and loss are configurable (corrupt_prob, loss_prob).

## Protocol Properties Guaranteed

Despite operating over an unreliable channel, the protocol guarantees:
- Reliable data delivery
- In-order delivery
- No duplicate delivery
- Automatic recovery from frame loss and corruption
- Flow control via sliding window
- Support for full-duplex communication

## Important Modeling Observation

The sender states IDLE and ACTIVE are logical states.
They are not implemented as explicit variables, but are derived from:
- base
- next_seq
- retransmission buffer state
- timer state

This approach reflects real protocol implementations and avoids unnecessary state variables.
