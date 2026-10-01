# Calibration helper nonzero state path

The body [7BC0,7CEE) is 302 bytes, followed by alignment and two literals. Decode the descriptor from the fifth stack argument, select stride144 record and stride60 row, and obtain the peripheral base through configuration word8 then word0. Call6AC0(5,descriptor) and retain its status. These324 fixtures supply a nonzero status, so the acquisition helpers6928/7288/6980 are not reached. The record mode+123 is zero and packet index is zero, selecting descriptor word40 packet data.

Read peripheral word+3200 low16 bits, clear peripheral control bit31, and initialize output with literal65535. Let n be packet word20 bits16..27. Adjustment is ((n+4)>>2) times96 when row byte33 lowbits equal2, otherwise times2. Subtract1 from adjustment for that mode with record mode1/10, or when n+1 is even. Multiply wrapped (raw-adjustment) by record byte132. If product<65536, store its low16 bits as output; otherwise retain65535. Force output1 if zero. Return retained state status and restore64-byte frame.

Original instructions and independent arithmetic agree in324 fixtures. Zero-state acquisition path, mode123==7 pointer path, helper clobbers and physical behavior remain unresolved. Synthetic MMIO and controlled state helper are explicit. No canonical admission or C implementation.
