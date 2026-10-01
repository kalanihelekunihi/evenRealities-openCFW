# Independent review 2003

**Result:** PASS_SCOPED.

- The original source hash and candidate artifact pins match the receipt. The owned spans are A374..A382 and A388..A3A4; alignment and literal data remain outside the code spans.
- Isolated replay reproduced all 48 fixtures exactly. Each fixture executes the original memory/register operations and stops at the WFI instruction to observe register/peripheral state; the harness then models continuation at (PC+2)|1.
- A374 clears bit 2 at literal[A384]+16 before WFI. A388 zero-extends the halfword at literal[A3A4]+338, stores it at literal[A3A8]+4, then sets bit 2 at literal[A3AC]+16. Both preserve R0/SP/PRIMASK as stated.

**Limits:** Wake continuation is synthetic. The fixtures do not demonstrate physical WFI sleep/wake, interrupt arrival, timing, or hardware register effects. No canonical admission is made.
