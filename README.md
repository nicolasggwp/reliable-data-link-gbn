# Reliable Data Link Protocol (Go-Back-N)

## Overview

This project implements a **reliable data link layer protocol** for **full-duplex communication** over an **unreliable point-to-point channel**.

The protocol is based on a **sliding window mechanism** using **Go-Back-N ARQ**, combined with **cumulative acknowledgments**, **timeouts**, **retransmissions**, and **piggybacking** of ACKs on data frames.

The implementation is a **user-level simulation written in Python**, designed strictly for educational purposes.  
It focuses on **data link layer fundamentals**, not on performance optimization, real hardware integration, or interaction with higher-layer protocols.

The main goal of this project is to understand **how reliable communication can be built on top of an unreliable channel**, using classic data link layer techniques.

---

## Design Goals

- Prioritize **simplicity and clarity** over maximum throughput
- Implement **Go-Back-N ARQ** to reduce protocol and buffer complexity
- Assume a **low-latency but unreliable channel**, making retransmission-based reliability feasible
- Keep the protocol strictly at the **data link layer**
- Use **raw bytes only**, avoiding higher-level abstractions

---

## Protocol Features

- Full-duplex communication
- Sliding window protocol (window size = 7)
- Go-Back-N ARQ retransmission strategy
- Cumulative acknowledgments
- Piggybacking of ACKs on data frames when possible
- Simple checksum for error detection
- Timeout-based retransmissions
- Sender-initiated transmission (no explicit connection setup)
- No buffering of out-of-order frames at the receiver

---

## Assumptions

- The communication channel is **unreliable**
- Frames may be:
  - lost
  - corrupted
- Channel latency is assumed to be low
- Bandwidth and throughput are not explicitly modeled
- The protocol focuses on **correctness and reliability**, not efficiency

---

## Frame Format

Each frame is transmitted as a sequence of raw bytes with the following logical structure:

| Type | Seq | Ack | Length | Payload | Checksum |

### Field Description

| Field    | Size        | Description |
|---------|------------|-------------|
| Type     | 2 bits      | Frame type (DATA or ACK) |
| Seq      | 3 bits      | Sequence number (modulo 8) |
| Ack      | 3 bits      | Cumulative acknowledgment number |
| Length   | 1 byte      | Payload length in bytes |
| Payload  | 0–255 bytes | Generic data from the network layer |
| Checksum | 1 byte      | Simple checksum for error detection |

The checksum is computed as a simple byte-sum modulo 256 over the entire frame, excluding the checksum field itself.

---

## Protocol Operation

### Sender

The sender implements a **sliding window protocol using Go-Back-N ARQ**.

- Frames are transmitted whenever:
  - data is available from the (simulated) network layer
  - there is space in the send window
- Each frame is assigned an increasing absolute sequence number internally, which is encoded modulo 8 in the transmitted frame header.
- The sender maintains:
  - `base`: sequence number of the oldest unacknowledged frame
  - `next_seq`: next sequence number to send
  - a buffer of unacknowledged frames

The sender uses **a single timer**, associated with the oldest unacknowledged frame:

- When this frame is sent, the timer starts
- If an acknowledgment advances the window:
  - the timer is restarted if outstanding frames remain
  - the timer is stopped if all frames are acknowledged
- On timeout:
  - all frames currently in the window are retransmitted
  - this follows the Go-Back-N strategy

Acknowledgments are **cumulative**.  
An ACK for sequence number `n` confirms reception of all frames up to `n`.

---

### Receiver

The receiver expects frames **strictly in order** and maintains the sequence number of the next expected frame.

When a frame is received:

1. The checksum is verified
2. The sequence number is checked

- If the frame is **correct and in order**:
  - the payload is delivered to the (simulated) network layer
  - the expected sequence number is incremented
- If the frame is **corrupted or out of order**:
  - the frame is discarded
  - no buffering of out-of-order frames is performed

The receiver always acknowledges the **last correctly received frame** using cumulative ACKs.

---

## Piggybacking

The protocol supports **piggybacking** for full-duplex communication.

- If the receiver has data to send in the opposite direction:
  - the ACK is included in the header of a DATA frame
- If no data is available:
  - a standalone ACK frame is sent

This reduces control overhead while preserving correctness.

---

## Error Handling and Flow Control

- Error detection is performed using a simple checksum
- Corrupted frames are discarded
- Out-of-order frames are discarded
- No explicit negative acknowledgments are used
- Reliability is achieved entirely through:
  - cumulative ACKs
  - sender timeouts
  - retransmissions

Flow control is enforced through the sliding window mechanism:
- The sender may transmit multiple frames without waiting for individual ACKs
- The receiver window size is effectively one, ensuring in-order delivery

---

## Unreliable Channel Model

The channel simulates real-world transmission issues:

- Random frame loss
- Random frame corruption (bit flipping)

This ensures that retransmissions, ACK handling, and timeouts are actually exercised during execution.

---

## How to Run (Simulation)

This project is intended for **educational and experimental purposes**.

1. Clone the repository
2. Run the main simulation script:

```bash
python3 main.py
```

The console output shows:

- frame transmissions
- acknowledgments
- corrupted and lost frames
- timeouts and retransmissions

Simulation parameters such as loss probability, corruption probability, window size, and timeout values can be adjusted in the code. 

### Simulation Output Notes

Because this project simulates a full-duplex data link layer protocol over an
unreliable channel, the console output may appear out of order.

This is expected behavior.

Frame transmissions, acknowledgments, piggybacked data, timeouts, and
retransmissions are triggered by independent events such as channel loss,
corruption, and sender timeouts. As a result, ACKs may appear before corresponding
"sent frame" logs, and retransmissions may occur even after successful deliveries.

The apparent ordering of log messages reflects the asynchronous nature of the
protocol simulation rather than incorrect protocol behavior.

---

## Limitations

- Receiver does not buffer out-of-order frames
- Simple checksum instead of CRC
- Go-Back-N retransmits the entire window on timeout
- No selective retransmission
- Assumes low-latency links

### Sequence Number Wrap-around Handling

Sequence numbers in this protocol operate modulo 8, as defined by the 3-bit
sequence number field in the frame header.

To correctly handle wrap-around, the sender internally uses **absolute sequence
numbers** for window management (`base`, `next_seq`, and retransmission buffer).
Modulo-8 sequence numbers are used **only for transmission and acknowledgment
encoding inside frames**.

When an ACK is received, the sender advances the window by matching the modulo ACK
value against the range of outstanding absolute sequence numbers. This avoids
ambiguity after wrap-around and ensures correct cumulative acknowledgment handling.

This design follows standard Go-Back-N implementations and prevents incorrect
window advancement across the modulo boundary.

---

## Why This Project

This project was created to deepen understanding of data link layer protocols.

Instead of relying on existing networking libraries, the protocol was implemented from first principles to explore:

- reliability mechanisms
- flow control
- error handling
- protocol design trade-offs

---

## Future Improvements

- Implement Selective Repeat ARQ
- Replace checksum with CRC
- Adaptive window sizing
- More realistic channel delay modeling
- Explicit separation of network and data link layers

---

## Documentation

A textual description of the sender and receiver state machines is available
in `docs/state_machine.md`.

---

Despite the non-deterministic ordering of log messages, the protocol guarantees
correct in-order delivery of data to the simulated network layer.
