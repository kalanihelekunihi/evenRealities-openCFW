# P2-20845 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 174 bytes at 0x47CDE2..0x47CE90; image/source hashes and raw tiling match, and the internal zero/nonzero branch resolves. The inherited 20-byte frame is popped on both routes: nonzero R7 performs another UDIV/MLS and UMULL borrow correction before recombining quotient/remainder words; zero R7 takes a distinct shift/merge path. The separate frameless CE3A entry performs a high-word division followed by four rolling 8-bit quotient stages; the last remainder MLS writes R2, unlike the prior R3 destinations. ARM register-shift semantics are preserved; no full arithmetic contract is claimed.
