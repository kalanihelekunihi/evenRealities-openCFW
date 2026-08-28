# G2 clock-manager divider production routing

The authenticated G2 2.2.6.10 bootloader and Apollo-main images contain the
same two closed clock-manager divider bodies.  The HFRC2 UQ17.15 calculator is
42 bytes at `0x00426C24`/`0x004D38EA`; the integer divider is 10 bytes at
`0x00426C4E`/`0x004D3914`.  Their complete-body SHA-256 identities and direct
bootloader callers are pinned by
`tools/analyze_g2_clkmgr_divider_candidate.py`.

`components/shared/ambiq/runtime_clkmgr_divider_candidate.c` is the MIT
clean-room semantic implementation.  Both routines fail closed on invalid
arguments with the Ambiq-compatible invalid-argument status value 6 and do not
mutate the destination on failure.  Valid inputs preserve the recovered ABI:
the HFRC2 routine computes `(requested / (source >> exponent)) * 32768`, and
the integer routine computes `requested / source`.

The compiled C is larger than the two stock spans, so production routing uses
reviewed Thumb `B.W` entry replacements:

- Apollo main appends both independently compiled, relocation-free leaves to
  the canonical overlay and redirects the two stock entries.
- The fixed-size bootloader places the leaves at `0x004176D4` and
  `0x0041772C`, inside authenticated generated-NOP space owned by the existing
  EasyLogger entry replacement, and redirects the two stock entries there.

Both placements are fail-closed: source, toolchain, function bytes, alignment,
stock entry spans, cave NOP bytes, and final provider hashes are pinned by the
component configurations and build reports.  This closes the software routing
gap without executing MMIO or changing physical clock hardware.  Electrical,
timing, and on-device behavior remain **blocked by unavailable physical
evidence** because no authorized G2 hardware is available in this workspace.
