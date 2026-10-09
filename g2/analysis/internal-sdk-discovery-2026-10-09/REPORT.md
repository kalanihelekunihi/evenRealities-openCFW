# Fresh internal-history SDK/dependency discovery

Scope: OpenCFW internal-history track only. Repository AGENTS/workflow/roadmap read; .agents/skills absent. Registry, consolidated hardware/library/toolchain references, symbols and the current discovery/audit packets checked before selecting new leads. Emulator inspection belongs to separate track. No campaign admission, registration/index/production/device edits.

## Substantive bounded result

New reference opportunity: TI-recommended OPT3001 driver as an OPT3007 protocol comparator. Hardware identity/path is already known, NOT new: Apollo ti_opt3007_assignRegistermap0x005135E0–0x00513734,340bytes and19 register triples; docs/hardware/components/opt3007.md already records register IDs and OPT3001/7 identification ambiguity. The registry/consolidated library list/current discovery reports inspected contain no OPT3001SW or Linux opt3001.c comparator. TI's official support explicitly says OPT3007/OPT3001 are software-compatible subject to fixed/configurable address difference. This makes a finite cross-device register comparator justified, not a guessed unrelated driver.

Acquired one official Linux source at immutable commitffc253263a1375a65fa6c9f62a893e9767fbebfa (v6.6 tag resolved through official repository API), SHA in acquisition.json. GPL-2.0-only SPDX retained; code not executed. Bounded check confirms register0x7E/0x7F, swapped16-bit I2C reads, exponent upper4bits/mantissa12bits and conversion-time constants100000/800000. These agree with the existing register-level device family. Linux IIO functions do not implement the stock19-triple assignRegistermap schema and no target byte/ABI/source match is claimed. Confidence high as protocol reference, low as stock source producer; payoff moderate for sensor conversion/endianness/caller interpretation, low for exact rebuild. Stop after schema/transport/value comparison; use stock driver bytes for any later source attribution.

Official sources: https://www.ti.com/tool/OPT3001SW-LINUX ; https://e2e.ti.com/support/sensors-group/sensors/f/sensors-forum/1247156/opt3007-does-opt3007-and-opt-3001-can-use-the-same-code ; https://github.com/torvalds/linux/tree/ffc253263a1375a65fa6c9f62a893e9767fbebfa/drivers/iio/light . TI's platform-independent example forum page was unavailable to web open; no attachment/license/source acquired, so that separate example is unvalidated rather than silently treated as available.

## Ranked other leads and exclusions

| Lead | Existing evidence / novelty | Confidence and payoff | Finite validation / stopping boundary |
| --- | --- | --- | --- |
| Macronix official low-level driver samples | Known MX25U25643G driver range starts0x0046F4A4; known RDID C2/25/39 and03/02/20/B7/6C command contract. Official software-support ANSI-C LLD package not found in inspected registry/reports | High availability of reference category; low stock provenance; moderate command-state payoff | Official page offers LLD category but inspected link loops to same page; no specific chip archive/license obtained. Need exact ZIP/version/license and compare bounded command/address/dummy/wait sequence; don't re-download known datasheet or infer producer from commands |
| Nested NationalChip multi_button/ADPCM sources | Already carried within acquired KWS/AIoT SDK, not new SDK; no stock address-bound interface discriminator established | Low current stock attribution; conditional low/moderate payoff | Require concrete stock symbol/state/constant fingerprint before a comparator; don't register or acquire redundant SDK |
| TDK ICT1531x/EDMP payloads | Already within registered invensense-icm45608 pin; hardware docs expressly cite them | High known reference; no new acquisition | Existing pin/data matching only if newly uncovered target; not new driver discovery |
| Major Apollo libraries and hardware docs | LVGL/FreeType/littlefs/nanopb/FlashDB/TinyFrame/Cordio/LC3/nPMX/Goodix/etc already indexed | Known; high reconstruction value but not new | Avoid duplicate family acquisition; selected producing configuration still distinct |
| Touch GNU/newlib/PDL/CRT | Recent audits supersede stale source inventory and older compiler ranges | Known selected source matches; no fresh family | Don't restart compiler matrices/Configure residuals |
| Case ST HAL/CMSIS | Official FLASH source/headers just acquired and tested, reversed names confirmed | Known new packet, not new lead | Producing project/compiler flags remain missing; no justified arbitrary GNU sweep |
| EM QP/C/LOG2/vendor ports | Official QP/C already acquired; vendor extension encoding known | Known; arithmetic source gap high payoff | Exact LOG2_Extension model/spec plus stock4.2 compatibility; do not treat software fallback as hardware truth |
| Codec CPU visibility | DMA mapping known but stock CPU bytestores | Known unresolved contract | Authenticated CPU alias/translation spec; no redundant root scans |
| IAR/Nema/controller/private model | Licensed/private limitations recorded | Specific high-payoff external inputs, not new publicly found SDK | Authentic vendor/producing sources/configuration, not generic substitutes |

Macronix official reference: https://www.mxic.com.tw/en-us/support/design-support/Pages/software-support.aspx . Generic Macronix LLD existence does not authenticate MX25U25643G-specific sample support or license.

No high-confidence newly identified stock-linked source family is claimed. One newly acquired protocol comparator and one concrete official sample-source acquisition lead survived known-input deduplication. Remaining unanchored symbol populations are not proof of additional third-party packages. Parent/auditor can compare these leads with emulator findings; don't declare global public-source exhaustion.
