# G2 Apollo clock-manager divider source candidate

The bootloader bodies at `0x00426C24..0x00426C4D` (42 bytes) and
`0x00426C4E..0x00426C57` (10 bytes) are byte-identical to Apollo-main bodies at
`0x004D38EA` and `0x004D3914`. Their main-image callers are the recovered
Apollo510 clock-manager configuration paths, and the authenticated AmbiqSuite
5.1.0 header exposes the matching `am_hal_clkmgr_clock_config` contract.

The authenticated public AmbiqSuite tree does not contain `am_hal_clkmgr.c`, so
this admission does not claim an exact public generating implementation. The
MIT clean-room candidate implements the two observed semantic operations:

- HFRC2 source prescaling followed by a UQ17.15 requested/source coefficient;
- HFRC requested/source integer division.

Unlike the stock leaf bodies, the candidate checks null outputs, zero divisors,
invalid shifts, and out-of-range floating conversion before mutating output. It
returns the Ambiq-compatible invalid-argument value 6 on those paths. Host
behavior and a freestanding Cortex-M55 hard-float object with zero undefined
symbols are gated by tests.

The candidate is not production-routed. Exact ABI/context binding, reviewed
dual-image placement, and authorized-device behavior remain blocked by
unavailable physical evidence. No hardware, MMIO, signing, flashing, or
publishing operation was performed.
