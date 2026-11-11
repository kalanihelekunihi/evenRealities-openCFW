# Sim vs hardware boot gap (openCFW, 2026-11-01)

**2026-11-11 update:** Apollo-main cstartup now copies the source-emitted
24-byte overlay to ITCM `0x40..0x58`; its linked bytes match the recovered
locked image. The missing-overlay lead below is historical. Hardware boot
remains unverified. See
[`apollo-itcm-overlay-startup-20261111.json`](../../evidence/apollo-itcm-overlay-startup-20261111.json).

openCFW main boots cleanly in the Renode simulator (it reaches the BLE stack),
but hangs **early** on real G2 hardware: no BLE advertising and no case
product-test frame, both temples identical, and RAM-init Fix 43 did not help.
The sim reaching BLE while hardware shows nothing means the hang is *earlier*
than anything the sim exercises faithfully — in early bring-up the sim fakes.

## What the simulator fakes (the gap surface)

From `~/Repo/g2-firmware-emulator/renode/boot.resc` and peripheral models:
- **ITCM 0x40 overlay is preloaded** (`generated/boot/itcm.bin`, derived from
  the app). On hardware the app's own cstartup must place the 24-byte helpers
  there. The 24 bytes are two leaf routines: a busy-delay (`subs r0,#1;bne;bx lr`)
  and a word-copy (`ldr r3,[r0],#4;str r3,[r1],#4;subs r2,#1;bne;bx lr`).
- **No NOR-flash model** in the attached peripherals (MSPI0 is the JBD display
  with open-bus reads). The real MX25U NOR is only lightly stubbed.
- The MRAM controller model "does not fake a successful boot operation"
  (`docs/apollo510-mram-control.md`); OTP is a synthetic fixture.
- Clocks/regulators/ADC are modeled leniently (status bits read ready, canned
  samples), so any poll that waits on a real conversion/lock is satisfied
  instantly in the sim.

## Leads, ranked

### Lead B — ADC FIFO unbounded poll (ROOT-CAUSE FIX APPLIED) ✅
`app/a-41-board-config/board_config.c` `board_hw_version_detect_509134`, called
from `board_init_5093ac` (init-table priority 1, **pre-scheduler**), spun in
`while (((ADC_FIFO_REG >> 20) & 0xff) == 0) {}` with **no timeout**, waiting for
the hardware-id ADC conversion. The lenient sim satisfies FIFO COUNT on the
first read; real silicon needs the ADC actually clocked, powered, triggered and
producing a slot-3 sample. If our ADC bring-up differs from stock (or depends on
a clock the sim doesn't gate), COUNT stays zero forever and the whole boot hangs
before any service — exactly the observed symptom. This is the only unbounded
hardware poll in the reconstructed pre-scheduler path (both audit passes agree).

**Fix 51 (board_config.c):** bound the poll (`HWID_ADC_POLL_LIMIT`); on timeout
default to the nPM1300 board profile (board_type 1, hw_version 0xff) and let
boot continue instead of bricking. In the sim the FIFO is ready on iteration 1,
so behaviour is unchanged (no regression). This breaks the brick even if the ADC
genuinely never converts; the true ADC-config root cause (if any) is only
observable once we can boot + read logs on hardware — see below.

### Lead C — littlefs assert / MSPI read config (NOT yet fixed; post-scheduler)
`storage/u-02-littlefs-config/g2_lfs_defines.h` has `LFS_ASSERT` ON, and
`__aeabi_assert` (IAR) does not return. The sim's NOR is blank (mounts clean);
real NOR holds months of stock littlefs+FlashDB, and with the version skew
(littlefs 2.10.1, FlashDB 2.0.0 vs stock 2.1.1) a mount-time invariant could
fail → infinite abort. Also suspect: the XIP control request numbers 18/21
("stock numbering", flagged as possibly two off the pinned Ambiq 5.1.0 enum) in
`drivers/flash/C1-mx25u-init/mx25u_mspi_init.c`, and the 4QOR (0x6C) dummy-cycle
/ NULL-devcfg mode-byte quirk in `drivers/flash/p-03-nor-mx25u/nor_mx25u_wrappers.c`,
which could make real quad reads return shifted garbage (sim returns canned data).
Littlefs mounts in a storage thread, so this would hang/abort just after the
scheduler — still before BLE/product-test. Chase this if Fix 51 is not enough.

### Lead A — ITCM 0x40 overlay missing from our region table (NOT fixed; low confidence)
Stock's IAR scatter table (0x75D3C8..0x75D410) has 5 records, one of which
places the 24-byte ITCM helpers at 0x40 (`findings-cross-cutting.md:282`,
`findings-codec-em9305.md:989`, scatter descriptor in `stock_ram_cells.c`
`g2_stock_ram_20000630` = {…,0x40,0x18,…}). Our reconstructed region table
(`runtime/g2c-gnu/g2c_gnu_init.c`) has 4 rows and populates **nothing** at ITCM
0x40. The sim masks this by preloading itcm.bin. However, no caller of ITCM
0x40/0x48 was found in the reconstruction, and the sim boots with ITCM 0x40
zeroed — so this is a real reconstruction gap but probably not the hang. Worth
closing (add a copy row) if a caller turns up or Fix 51 + Lead C don't resolve it.

## How to confirm (needs hardware feedback)

The sim cannot prove any hardware fix (it boots regardless). Confirmation needs
to boot openCFW on a temple and observe. That is exactly why the next step is
the **self-recovery / early-arm experiment** (see
`reference/self-recovery-arming.md`): arm SBL wired-recovery in early board_init
*before* this hang point, so a flash that still hangs leaves a recoverable temple
and lets us iterate. Only then can we read whether the ADC timed out (Lead B
root cause) or the hang moved to storage (Lead C).
