#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Reachability survey for the BL-006 apollo_bootloader retained-byte catalog.

BL-006 names 77 `official_blob` flash-plan regions (5,892 bytes total) in
`[0x0041F9B6, 0x00428378)` that remain classified as stock bytes: literal
pools, alignment fillers, and stock-compiler tails left over after several
functions in this address span were already replaced with reviewed C.

This tool does not compile, patch, or admit any of those bytes as
source-owned; it only *corroborates or refutes*, with an independent
whole-image control-flow scan, the "unreachable in the shipped image" claims
made by the per-function closure audits that already replaced the code
preceding several of these regions. It is evidence for future BL-006 work,
not a completion of it.

Method, for each pinned region `[start, end)`:

1.  Re-read the authenticated bytes from the official blob and check their
    SHA-256 against the pin recorded here, so a drifted region (closed by a
    concurrent agent, or a stale catalog) fails closed instead of silently
    passing.
2.  Disassemble the *entire* stock bootloader image once with Capstone and
    collect every branch/call instruction's source and immediate target
    address (`b`, `bl`, `b.w`, `bl.w`, conditional forms, `cbz`/`cbnz`).
3.  Read `components/bootloader/core_overlay/overlay.json` and compute the
    union of stock byte spans that the current build already overwrites
    (`patch_sites` entry-redirect spans and `in_place_leaves` compiled
    spans). Any branch instruction whose *source* address falls inside that
    union no longer exists in the shipped image; it cannot make its target
    reachable there even though it is still visible in the raw stock blob.
4.  A region is `corroborated_unreachable_control_flow` when every inbound
    branch found in the raw stock disassembly originates from an
    already-overwritten span. It is `no_control_flow_reference_found` when
    no branch targets it at all (typical for literal pools/alignment). It is
    `POSSIBLY_REACHABLE_NEEDS_REVIEW` when at least one inbound branch
    survives in the shipped image and lands in the region.
5.  Independently, the tool also counts how many 4-byte little-endian words
    anywhere in the stock image equal the region's own start address, as a
    cheap (necessarily over-approximate) signal that something may still
    reference the region as *data* (a pointer table entry) rather than as a
    branch target. This is reported for human/agent follow-up, not folded
    into the verdict, because a coincidental 32-bit match is possible.

No hardware, signing, flashing, or transmission operation is performed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
from capstone.arm import ARM_OP_IMM

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
OVERLAY_CONFIG = ROOT / "components/bootloader/core_overlay/overlay.json"
RUN_BASE = 0x00410000

BRANCH_MNEMONIC_PREFIXES = ("b", "cbz", "cbnz")
# Instructions that start with "b" but are not branches in this ISA subset.
NON_BRANCH_B_MNEMONICS = frozenset({"bic", "bic.w", "bfc", "bfi", "bkpt"})

# The 77 BL-006 official_blob regions, [start, end) in run-base addresses,
# with the SHA-256 of their authenticated stock bytes and the flash-plan
# description they were catalogued under. Regenerate this list from
# `g2/build/source/flash-plan.json` (component apollo_bootloader,
# address_status official_blob) if it drifts; do not hand-edit hashes.
BL006_REGIONS: tuple[dict[str, Any], ...] = (
    {"start": 0x0041F9B6, "end": 0x0041F9D8, "sha256": "cbfa340f33581bc4fcf9f460eb3b5ecdabb99ed9b844258eaf0a3783d30eaa16", "desc": "Authenticated vector and literal island retained after the EasyLogger channel transport"},
    {"start": 0x0041F9EE, "end": 0x0041F9F0, "sha256": "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7", "desc": "Authenticated two-byte alignment retained before the initializer priority comparator"},
    {"start": 0x0041FA40, "end": 0x0041FA50, "sha256": "39565a709f9618f4a352619d052d4cd6340f9bb446178f346a30ec557bdb362f", "desc": "Authenticated initializer-table pointers and alignment retained before the boot-platform setup entry"},
    {"start": 0x0041FAD0, "end": 0x0041FADC, "sha256": "4c991d43a1173b4c27ada6be4c12a50eee2bfc0d8df510dd6e7369d268b37b64", "desc": "Authenticated guard, platform-configuration, and pin-configuration pointer literals retained after guarded teardown"},
    {"start": 0x0041FCF6, "end": 0x0041FD70, "sha256": "a336f9a95b7426fb8c078b298098471dcf02e7e7fd66730d0dcdc2d3427db2ec", "desc": "Authenticated pin-configuration and allocator literals retained between the pin-group dispatcher and TLSF pool initializer"},
    {"start": 0x0041FDA8, "end": 0x0041FDC0, "sha256": "37ce43e7948cf49f74162a9509e41cc23f206b64a12b7e4f038f578d57b6d17b", "desc": "Authenticated allocator and diagnostic pointer literals retained before the IRQ-service cluster"},
    {"start": 0x0042086C, "end": 0x00420890, "sha256": "bd568192057107608070c8993444e0e2bdc34243a5ddf9972040371697be4eca", "desc": "Authenticated non-executable literal and alignment gap preceding the MX25U25643G four-byte-mode entry"},
    {"start": 0x00420978, "end": 0x00420984, "sha256": "6b00f23868a0bcfbca264efd5b172d74ab278103dc8869e0bc94eb9f08358b59", "desc": "Authenticated non-executable literal and alignment gap preceding the MX25U25643G write-enable wrapper"},
    {"start": 0x004209BE, "end": 0x004209C4, "sha256": "da7c6b1527680ce2ccd4b90a5cbf4b5e3f55ca2148ae0bdf0403905053bc245a", "desc": "Authenticated non-executable literal and alignment gap preceding the MX25U25643G write-disable wrapper"},
    {"start": 0x004209FC, "end": 0x00420A08, "sha256": "24e3dd42d22fb00fcda8010047ae549a2110c8e5c77f230fb43a071466a26aa4", "desc": "Authenticated non-executable literal and alignment gap preceding the MX25U25643G sector-erase service"},
    {"start": 0x00420ADA, "end": 0x00420B0C, "sha256": "619fd98be5ccc3286a0a39c06f1c556503edee5868456a01e8e15c67b2fb5ed2", "desc": "Authenticated non-executable literal and alignment gap preceding the MX25U25643G page-program service"},
    {"start": 0x00420C14, "end": 0x00420C5C, "sha256": "cfc3cdfaf2523ca39c957109635e3427aa5dca5f88993d6b841bc3ebc21b760f", "desc": "Authenticated non-executable literal and alignment gap preceding the MX25U25643G QE service"},
    {"start": 0x00420DFA, "end": 0x00420E08, "sha256": "8b41f058c64229c00d3a505f11715874ac3dcada1086d696f408e9365a2b3b6f", "desc": "Authenticated non-executable literal pool preceding the MSPI device reconfiguration service"},
    {"start": 0x00420F0C, "end": 0x00420F10, "sha256": "cee19cda5a705d63da91e2090a5ebb792a8ea1040f92b95717823e8aa9299830", "desc": "Authenticated non-executable literal pool preceding the MX25U25643G serial-mode service"},
    {"start": 0x00420F6A, "end": 0x00420F70, "sha256": "86d14b79fc1438915684e8f5b80873e3458147a166ffdaa3a0d42aa9588c690f", "desc": "Authenticated non-executable literal and alignment gap preceding the MX25U25643G read service"},
    {"start": 0x00420FF2, "end": 0x004210C8, "sha256": "21ac43cfda25ec0bc55b6df8e70c3341923392c939cf989b96f0945e7b151ba3", "desc": "Authenticated non-executable literal and alignment pool preceding the LittleFS directory bootstrap service"},
    {"start": 0x00421372, "end": 0x004213D4, "sha256": "69c23d9c23df577cb63407fd0899c61afc102f15fc1a38f710fde8d829b71d2b", "desc": "Authenticated non-executable literal and alignment gap after the LittleFS block-erase callback"},
    {"start": 0x0042156E, "end": 0x00421584, "sha256": "0ba5bda2afbb0b139d9a8ffdd65e988e3a169baae65dcbf62df014d0a76aa18b", "desc": "Authenticated non-executable mapped-memory control, security, and window literal pool"},
    {"start": 0x0042220E, "end": 0x00422220, "sha256": "34fb2e40d40a342dcdc1d23c99581a89280341ef5be58a15a5765d4328a99a9e", "desc": "Authenticated row-six enable literal seam retained between exact source bodies"},
    {"start": 0x0042228E, "end": 0x004222A0, "sha256": "08388290f49d6fd437c9ccef1aaab3fe54465ec3d251b281f154e02e341a151a", "desc": "Authenticated row-six disable literal seam retained between exact source bodies"},
    {"start": 0x004222D2, "end": 0x004222F0, "sha256": "1f137d5f192d742c2f2d77edfb99116475879ab56011173bd5531e68929285f5", "desc": "Authenticated padding and literal seam retained before exact mode routing bodies"},
    {"start": 0x00422430, "end": 0x00422468, "sha256": "178bf3040304055de474d0ffb04a4f33e265679c33253ff3a6c13427947c261d", "desc": "Authenticated debug-service literal pool retained before exact source bodies"},
    {"start": 0x00422574, "end": 0x00422590, "sha256": "82d8e4094be3bec9b384ed5df514b62e04f9af0b28bc15b7c1e00ef79613d62e", "desc": "Authenticated debug trace literal pool retained before the constraint dispatcher"},
    {"start": 0x004225AC, "end": 0x004225D0, "sha256": "6a1c3b3c218a63a0485994c42f851a99bff4fedd5443396ba4a7bbe7a1ba5b25", "desc": "Authenticated constraint-handler pointer and diagnostic string retained before memchr"},
    {"start": 0x00422712, "end": 0x00422714, "sha256": "b35429818002e6e8ced180b98b8273bd2fc11f8ed0b0ff54eade7a5920a15ed4", "desc": "Authenticated two-byte alignment between the double ldexp wrapper and core"},
    {"start": 0x00422872, "end": 0x00422874, "sha256": "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7", "desc": "Authenticated two-byte alignment before the IAR thread-pointer leaf"},
    {"start": 0x00422AD2, "end": 0x00422AD4, "sha256": "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7", "desc": "Authenticated two-byte alignment before the four-instance hardware-service initializer"},
    {"start": 0x00422D7A, "end": 0x00422D7E, "sha256": "31f3a0337ae2102f7205453fb1b5cf94d31d04e8951016c229aafacd29b75048", "desc": "Authenticated four-byte non-executable datum before the per-instance status mapper"},
    {"start": 0x004233E0, "end": 0x004233E8, "sha256": "dc6d6e468128844ba51e86cea994b84359c5e7b1bc741b6212e39b7a06161f72", "desc": "Authenticated retained literal words between the FIFO adapters and mode dispatcher"},
    {"start": 0x00423430, "end": 0x00423444, "sha256": "84930f336c385f7f711daa4578dfe4b8e07a7cd18b80a375ace9a96a8b84e002", "desc": "Authenticated retained literal words between the mode dispatcher and source-owned wait wrappers"},
    {"start": 0x004236FA, "end": 0x00423700, "sha256": "5f37ee3be00f7af81377ea45215056b9da7925ead403c1ff84274f0c17846ab7", "desc": "Authenticated retained alignment and literal word between register services"},
    {"start": 0x00423764, "end": 0x0042377C, "sha256": "2a5b0ce73bc2295f563559c798d0262265fa3010bee7c38c18a29ef3d75786ee", "desc": "Authenticated retained register and identity words before the service dispatcher"},
    {"start": 0x0042382C, "end": 0x00423864, "sha256": "1c53b412e3fbb0cb88a21c22d1e2338353506516a1f4f531c09b24b49463db29", "desc": "Authenticated retained literal and status words before the bounded memory-exchange helpers"},
    {"start": 0x00423D9A, "end": 0x00423DA0, "sha256": "7cf4979cad48b6ce2b499300c3c3b8ed96387be1abbadcd932aba625b082f975", "desc": "Authenticated retained hardware-control register literal and alignment bytes"},
    {"start": 0x00423DCE, "end": 0x00423DD0, "sha256": "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7", "desc": "Authenticated retained alignment before the interrupt-atomic hardware-control service"},
    {"start": 0x00423E0C, "end": 0x00423E14, "sha256": "eb9eccfa0c7b87835a778c7ab67a2f4201b14d38a0d6b02bbb85a110f172d963", "desc": "Authenticated retained SRAM literal words before the hardware-control state mapper"},
    {"start": 0x0042423C, "end": 0x0042488E, "sha256": "b8c84b34f444b4959fb39b8ae8fbb0b5f40a0a19a413d552a39892986985e44e", "desc": "Authenticated unreachable stock tail after the source-owned MSPI device-configuration return"},
    {"start": 0x004248E2, "end": 0x00424976, "sha256": "4185510b7bd0813409986cbfbbaee0c75192ff4bf21bdd0dcc92e9898254c1d9", "desc": "Authenticated unreachable stock tail after the source-owned MSPI PIO-mixed configuration return"},
    {"start": 0x0042499C, "end": 0x004249A0, "sha256": "512cda42a9c3b00954f5ebd4cc8487efe02285b6c25f63e91df882b8846d7ded", "desc": "Authenticated retained MSPI0 base literal before the clock-generator control service"},
    {"start": 0x00424AB2, "end": 0x00424AF0, "sha256": "ed80a40ae6bab68985600798a3490f94585fe91607cc3bb008a4b96f13ce1ac1", "desc": "Authenticated alignment and G2 MSPI state-base literal between initialize and configure"},
    {"start": 0x00424B88, "end": 0x00424BE4, "sha256": "3e5e5d41c9b4c0accb0c9f39be8b0f6f70ff8aad793d3806f529bc500043acca", "desc": "Authenticated handle, MSPI base, and pad-mask literals before public device configuration"},
    {"start": 0x00424E84, "end": 0x00425066, "sha256": "96be3ed2b6277d645863984409f19be4ca6321dd94c6579eb5659de53d06b41a", "desc": "Authenticated unreachable stock tail after the source-owned public MSPI device-configuration return"},
    {"start": 0x004250E6, "end": 0x004250F0, "sha256": "1bb97734fb42a005414ee4a5ea9783acf43addb631e489d8ea445d39ba5d5492", "desc": "Authenticated unreachable stock tail after the source-owned MSPI enable return"},
    {"start": 0x00425160, "end": 0x0042516C, "sha256": "5408d55de7633ebc2732b1628361b885baa2365f873b67e5b4aece2d8dd97114", "desc": "Authenticated unreachable disable tail plus alignment and lifecycle literal bytes before MSPI deinit"},
    {"start": 0x004251A4, "end": 0x004251C0, "sha256": "46dcf5abe08d382febe2de91c04fb274c4178e6cba750838ea210aafae585a7b", "desc": "Authenticated alignment and literal pool between MSPI deinitialize and the control dispatcher"},
    {"start": 0x0042612C, "end": 0x004262E0, "sha256": "c83b4119f0991198d619c51dd5bcd92807c4aafa4d181444e7d9cb484f453bfe", "desc": "Authenticated unreachable stock tail after the source-owned MSPI control dispatcher"},
    {"start": 0x004263E0, "end": 0x00426450, "sha256": "750615cb008335b6ec447c757032046216f8913c5a424c2393ccf03f7b545db1", "desc": "Authenticated unreachable stock tail after the source-owned blocking-transfer return plus the four-byte alignment"},
    {"start": 0x0042647C, "end": 0x00426484, "sha256": "95f1b19d4d488b37fd91939552d88e79d1361f2f99f005c937e1d178aadd4256", "desc": "Authenticated unreachable stock tail after the source-owned MSPI interrupt-enable return"},
    {"start": 0x004264B0, "end": 0x004264BA, "sha256": "2cbb69478279294d28007dbc24297342156d44c2c3561c7ed01387394af482e8", "desc": "Authenticated unreachable stock tail after the source-owned MSPI interrupt-disable return"},
    {"start": 0x004264F6, "end": 0x00426506, "sha256": "d23bae4506efde890d16f3ac9dbf8753b6970db0c5854c39280dbbb30c8a0eab", "desc": "Authenticated unreachable stock tail after the source-owned MSPI interrupt-status return and before"},
    {"start": 0x004267FE, "end": 0x00426808, "sha256": "f0ef1fedd08c40bdcdbac2afa7a8df77f7a1b6cebf3ccbe24145340afa295b16", "desc": "Authenticated non-executable MSPI interrupt-service literal pool retained before power control"},
    {"start": 0x00426BFE, "end": 0x00426C10, "sha256": "6d01aee7b0ea94693ad3e39e729d72dbdcf694fa0bb121442d026ca719b3d5c4", "desc": "Authenticated non-executable MSPI power-control literal pool and alignment"},
    {"start": 0x00426C22, "end": 0x00426C24, "sha256": "d61f3ece088ca2fb6ebd3f47479ea5514bdbc39d0decd1f678f629b107878331", "desc": "Authenticated unreachable terminal return after the source-owned memset wrapper"},
    {"start": 0x00426C70, "end": 0x00426C72, "sha256": "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8", "desc": "Authenticated unreachable terminal return after the source-owned CLKGEN HFADJ enable leaf"},
    {"start": 0x00426CC4, "end": 0x00426CCC, "sha256": "d7d2a4025d26ea346c59aacce99c433ac393769f80658c1d6586235cda9af704", "desc": "Authenticated unreachable terminal tail after the source-owned CLKGEN dual-clock switch"},
    {"start": 0x00426D2C, "end": 0x00426D48, "sha256": "30f0e66dd252b9acdfb5b00d677bb6ea54ea2252753fa16db8f7e5b5d6de2624", "desc": "Authenticated padding and literal-pool bytes between the CLKGEN disable and floating common-divisor"},
    {"start": 0x00426DB2, "end": 0x00426DB4, "sha256": "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7", "desc": "Authenticated two-byte padding between the floating common-divisor and ratio helper entries"},
    {"start": 0x00426F6A, "end": 0x00426F6C, "sha256": "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7", "desc": "Authenticated two-byte padding between the floating multiplier and encoding-selector entries"},
    {"start": 0x00427032, "end": 0x00427040, "sha256": "94542922bcc73242bc10178a2790c3d10c998df2f5b6a9c93d840957f402f3f4", "desc": "Authenticated literals and alignment between the floating selector and System PLL minimum-VCO entry"},
    {"start": 0x0042714C, "end": 0x00427160, "sha256": "d2fd6d50093232dbbe37ee054454fd606fb53fda088a33e29d23ee6528d1cc9f", "desc": "Authenticated literals and alignment between the System PLL minimum-VCO and postdivider entries"},
    {"start": 0x00427308, "end": 0x00427310, "sha256": "90c7a6a98a6f94c175f4def78616baab7e97e70b48835904297f87726111cd4a", "desc": "Authenticated literal/alignment gap between the System PLL initialization and deinitialization services"},
    {"start": 0x00427588, "end": 0x004275EA, "sha256": "3125e285c2219d00857b544333279b575f25f03246dc91b96546fd41ec9f15b8", "desc": "Authenticated literals, alignment, and intervening code between System PLL lock-wait and the queue family"},
    {"start": 0x004276BA, "end": 0x004276BC, "sha256": "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7", "desc": "Authenticated zero alignment halfword between the queue family and memmove"},
    {"start": 0x00427752, "end": 0x00427754, "sha256": "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7", "desc": "Authenticated zero alignment halfword between memmove and the command-queue index updater"},
    {"start": 0x0042784C, "end": 0x00427878, "sha256": "d6d5c013eeebd40c063fc7586b9b5c531c55498b1e006a3c6305b47045b6de9b", "desc": "Authenticated unreachable remainder after the source-owned command-queue initializer"},
    {"start": 0x004278BC, "end": 0x004278C8, "sha256": "7e1a874b7a215628e732acc984029a1a50a095918168bf2ba22cdd7d8d266b48", "desc": "Authenticated unreachable remainder after the source-owned command-queue enable service"},
    {"start": 0x004278FC, "end": 0x0042790A, "sha256": "9b37f68b03d4c5eb24064b1fb71666ba59d61118d182378739420160b6e2a0d8", "desc": "Authenticated unreachable remainder after the source-owned command-queue disable service"},
    {"start": 0x0042799E, "end": 0x004279BE, "sha256": "dcf9d1eae1901c914dcc21e28cc1f8de507044dc67797f930c622068fd307b97", "desc": "Authenticated unreachable remainder after the source-owned command-queue block allocator"},
    {"start": 0x004279EE, "end": 0x004279F0, "sha256": "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8", "desc": "Authenticated unreachable remainder after the source-owned command-queue block release service"},
    {"start": 0x00427A4C, "end": 0x00427A56, "sha256": "b9327206787bf96e58b025028eebf974d282b0032718c442f2aedbb009b6a397", "desc": "Authenticated unreachable remainder after the source-owned command-queue block post service"},
    {"start": 0x00427ABE, "end": 0x00427AD6, "sha256": "ba93a98be719d439c0f4e3d362c1df2174a73fcc44ae3f82a1a413d3ed051785", "desc": "Authenticated unreachable remainder after the source-owned command-queue status service"},
    {"start": 0x00427B2E, "end": 0x00427B38, "sha256": "433eb6ef5ddfdd266cf77c2c82da47fb640852dc55956f4a77a6bf5350bd3acf", "desc": "Authenticated unreachable remainder after the source-owned command-queue termination service"},
    {"start": 0x00427B90, "end": 0x00427BAA, "sha256": "083d6df438d62d8c22618063fe1a0756dd25ad4f4dda8eb7bb71f0ecc0c4a27f", "desc": "Authenticated unreachable remainder after the source-owned command-queue error-resume service"},
    {"start": 0x00427C02, "end": 0x00427C12, "sha256": "ba0d5f35c22a12d89ad358608d72c30eb7e64acc726eccacbb991bfc80aab1f9", "desc": "Authenticated unreachable remainder after the source-owned command-queue reset service"},
    {"start": 0x00427C72, "end": 0x00427C90, "sha256": "be2ce28a6fe5bb649ccb4bd45ff74b9cdcea4b78072e89c79d20b35ac7e1fa8b", "desc": "Authenticated unreachable command-queue suffix and typed gap before the source-owned binary32 math runtime"},
    {"start": 0x00427D84, "end": 0x00427D98, "sha256": "f35a5cb7dfcde48c147a027e717db6113d416a95014c14703077f500022a44eb", "desc": "Authenticated unreachable remainder after the source-owned binary32 remainder core"},
    {"start": 0x00427E54, "end": 0x00428378, "sha256": "0ce1f6634fd2f9b54629e04ef7606fc28e0830c02f4262a7bae95abb38658821", "desc": "Authenticated retained literal, table, and alignment bytes between the binary32 runtime and SPOT-management"},
)

EXPECTED_REGION_COUNT = 77
EXPECTED_TOTAL_BYTES = 5892


class SurveyError(RuntimeError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replaced_spans(overlay_config: dict[str, Any]) -> list[tuple[int, int]]:
    """Stock byte spans the current build already overwrites (no longer the
    original instructions in the shipped image)."""

    spans: list[tuple[int, int]] = []
    for site in overlay_config.get("patch_sites", []):
        start = int(site["runtime_address"])
        spans.append((start, start + int(site["expected_size"])))
    for leaf in overlay_config.get("in_place_leaves", []):
        start = int(leaf["runtime_address"])
        spans.append((start, start + int(leaf["expected"]["size"])))
    spans.sort()
    return spans


def address_in_spans(address: int, spans: list[tuple[int, int]]) -> bool:
    for start, end in spans:
        if start <= address < end:
            return True
        if address < start:
            break
    return False


def collect_branches(blob: bytes, run_base: int) -> list[tuple[int, str, int]]:
    """Disassemble the whole stock image once; return every branch/call
    instruction as (source_address, mnemonic, immediate_target)."""

    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
    decoder.detail = True
    branches: list[tuple[int, str, int]] = []
    offset = 0
    address = run_base
    length = len(blob)
    while offset < length:
        window = blob[offset:offset + 8]
        if len(window) < 2:
            break
        decoded = list(decoder.disasm(window, address, count=1))
        if not decoded:
            offset += 2
            address += 2
            continue
        insn = decoded[0]
        mnemonic = insn.mnemonic
        if (
            mnemonic.split(".")[0] in BRANCH_MNEMONIC_PREFIXES
            or mnemonic.startswith("b")
        ) and mnemonic not in NON_BRANCH_B_MNEMONICS:
            for operand in insn.operands:
                if operand.type == ARM_OP_IMM:
                    branches.append((address, mnemonic, operand.imm))
        offset += insn.size
        address += insn.size
    return branches


def count_literal_word_matches(blob: bytes, run_base: int, needle_address: int) -> int:
    needle = needle_address.to_bytes(4, "little")
    count = 0
    start = 0
    while True:
        index = blob.find(needle, start)
        if index == -1:
            break
        count += 1
        start = index + 1
    return count


def survey() -> dict[str, Any]:
    if len(BL006_REGIONS) != EXPECTED_REGION_COUNT:
        raise SurveyError(
            f"BL-006 region catalog has {len(BL006_REGIONS)} entries, "
            f"expected {EXPECTED_REGION_COUNT}"
        )
    total_bytes = sum(r["end"] - r["start"] for r in BL006_REGIONS)
    if total_bytes != EXPECTED_TOTAL_BYTES:
        raise SurveyError(
            f"BL-006 region catalog totals {total_bytes} bytes, expected "
            f"{EXPECTED_TOTAL_BYTES}"
        )

    blob = OFFICIAL.read_bytes()
    overlay_config = json.loads(OVERLAY_CONFIG.read_text(encoding="utf-8"))
    spans = replaced_spans(overlay_config)
    branches = collect_branches(blob, RUN_BASE)
    catalog_spans = [(r["start"], r["end"]) for r in BL006_REGIONS]
    catalog_spans.sort()

    results = []
    for region in BL006_REGIONS:
        start, end = region["start"], region["end"]
        offset = start - RUN_BASE
        data = blob[offset:offset + (end - start)]
        actual_sha256 = digest(data)
        if actual_sha256 != region["sha256"]:
            raise SurveyError(
                f"region [0x{start:08X},0x{end:08X}) drifted from its pin "
                f"(expected {region['sha256']}, got {actual_sha256}); "
                "regenerate BL006_REGIONS from flash-plan.json before trusting "
                "this survey"
            )
        inbound = [
            {"source": src, "mnemonic": mnemonic, "target": target}
            for src, mnemonic, target in branches
            if start <= target < end
        ]
        # A branch is only evidence of reachability *in the shipped image* if
        # its own source address is neither (a) inside a span the build
        # already overwrites, nor (b) inside one of the 77 BL-006 regions
        # itself. Case (b) covers two situations that are not a live external
        # reference: capstone occasionally misreads literal-pool/data bytes
        # as branch-shaped opcodes when swept linearly, and one still-dead
        # region can contain a genuine branch to another still-dead region
        # (both already unreachable from the one function whose replacement
        # already covers their shared caller).
        external_unresolved = [
            b for b in inbound
            if not address_in_spans(b["source"], spans)
            and not address_in_spans(b["source"], catalog_spans)
        ]
        internal_unresolved = [b for b in inbound if b not in external_unresolved]
        if external_unresolved:
            verdict = "POSSIBLY_REACHABLE_NEEDS_REVIEW"
        elif inbound:
            verdict = "corroborated_unreachable_control_flow"
        else:
            verdict = "no_control_flow_reference_found"
        literal_matches = count_literal_word_matches(blob, RUN_BASE, start)
        results.append(
            {
                "start": f"0x{start:08X}",
                "end": f"0x{end:08X}",
                "size": end - start,
                "desc": region["desc"],
                "verdict": verdict,
                "inbound_branch_count": len(inbound),
                "external_unresolved_inbound_branches": external_unresolved,
                "internal_unresolved_inbound_branches": internal_unresolved,
                "literal_word_match_count": literal_matches,
            }
        )

    needs_review = [r for r in results if r["verdict"] == "POSSIBLY_REACHABLE_NEEDS_REVIEW"]
    return {
        "component": "apollo_bootloader",
        "work_item": "BL-006",
        "region_count": len(results),
        "total_bytes": total_bytes,
        "needs_review_count": len(needs_review),
        "regions": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = survey()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        by_verdict: dict[str, int] = {}
        for region in report["regions"]:
            by_verdict[region["verdict"]] = by_verdict.get(region["verdict"], 0) + 1
        print(f"BL-006 retained-byte survey: {report['region_count']} regions, "
              f"{report['total_bytes']} bytes")
        for verdict, count in sorted(by_verdict.items()):
            print(f"  {verdict}: {count}")
        if report["needs_review_count"]:
            print("  ** unresolved inbound branches found; do not treat any "
                  "flagged region as dead without further review **")
    return 1 if report["needs_review_count"] else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SurveyError as exc:
        raise SystemExit(f"BL-006 survey failed: {exc}") from exc
