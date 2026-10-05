# Adjacent SCB FIFO leaf: RX trigger level

## Scope and attribution

The selected leaf is `Cy_SCB_SetRxFifoLevel`, immediately following the SCB
array read/write helpers at runtime `0x9316`. In decoded image coordinates it
is `[0x6016,0x6042)` (44 bytes), SHA-256
`1fdc6e20657ebf1efbbf7423c354904526f55af9f31d09ad5cd700d69ecdb993`. The
decoded image is obtained by dropping the touch FWPK prefix `[0,0x20)` from
the official 34,464-byte payload and is SHA-256
`371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87`.

The pinned upstream source is Infineon PDL `release-v2.21.0`, git commit
`35f1714623cfea682d5e285af80d50416b4c7bbc`, Apache-2.0. Its [`cy_scb_common.h`
at the exact commit](https://raw.githubusercontent.com/Infineon/mtb-pdl-cat2/35f1714623cfea682d5e285af80d50416b4c7bbc/drivers/include/cy_scb_common.h)
declares the function and implements it at lines 810–827 using the trigger
level validity assertion and a clear/set field update. The source documents
the trigger-level meaning at lines 813–821. This is source and semantic
correspondence; this leaf was not compiled from PDL and no new exact-byte
upstream match is claimed.

## Recovered behavior

Disassembly of the authenticated original body shows:

- Read `[base + 0x000]`; if `config & 0xC000` is zero, depth is 16, otherwise
  depth is 8.
- If `level >= depth`, execute `BKPT #1` before reading or writing the target
  FIFO control register.
- Otherwise read `RX_FIFO_CTRL` at `base + 0x304`, clear its low byte, OR in
  `level & 0xff`, write the word back, then return.
- Register access order is config read, RX_FIFO_CTRL read, RX_FIFO_CTRL write
  on success; invalid-level cases read only config and stop at BKPT.

The bytes support the register offset, depth rule, validation branch, RMW, and
preservation of upper bits. The PDL source calls the low byte the trigger-level
field and describes threshold interrupt behavior; the relationship between
this field and actual interrupt firing has not been tested against hardware.
No FIFO clear operation is inferred or implemented in this cycle.

## New source helper and tests

[`touch_scb_fifo.c`](../../components/foundation/touch_scb/touch_scb_fifo.c)
and its header provide `touch_scb_fifo_set_rx_level(base, level)`. This new
checked API returns `TOUCH_SCB_FIFO_INVALID_LEVEL` for the original BKPT path
rather than raising a breakpoint. Valid calls perform the same depth test and
low-byte RMW. It requires a caller-supplied live mapped, aligned base and does
not configure or clear the FIFO.

`g2/tests/test_touch_scb_fifo.py` exercises 8- and 16-entry depth settings,
valid boundary values, high-bit preservation, invalid/high levels, and bad or
overflowing bases against simulated register memory. It also compiles a
freestanding ARMv6-M object.

Run the original-code test with the existing analysis environment:

```sh
~/.local/share/opencfw/venv/bin/python \
  g2/analysis/touch-mmio-cycle-2026-10-05/next-fifo/verify_original.py
```

The script has a `__debug__` fail-closed guard and creates `results.json`
exclusively so it cannot silently replace evidence. The saved result records
the authenticated firmware/image/function identities, source PC and original
instruction bytes for each executed step, synthetic-register read/write order,
and valid and BKPT cases. It executes only this 44-byte function against
RAM-backed words; no physical MMIO, hardware interrupt, timing, or FIFO data
movement is tested.
