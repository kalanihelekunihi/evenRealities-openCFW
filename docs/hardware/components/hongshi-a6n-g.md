# Hongshi A6N-G microLED panel

**Used in:** G2 glasses, per temple, as display panel variant 1 (selected
when the ULED config key byte is `0x06`). Tags:
[vocabulary](../README.md#confidence-vocabulary).

## Identification

| Evidence | Tag |
|---|---|
| Recovered "A6N-G" driver: bank/register/value init stream (50 B, 0xFF delay, 0xEE timer markers), chip register `0x06 == 0x01`, status preamble `02 00 2A 00 00 00 01 DF` | FW High (`g2/docs/research/g2-uled-a6ng-recovery.md`; `g2/docs/research/g2-uled-manager-recovery.md:50`) |

## Documents

No datasheet found. Public descriptions of Hongshi's "Aurora A6" microdisplay:

| Source | URL |
|---|---|
| CIOE 2024 showcase | https://www.ledinside.com/showreport/2024/10/2024_10_08_00 |
| Company profile | https://www.microled-info.com/hongshi-intelligence-tech |
| Mass production news | https://www.minimicroled.com/micro-led-chips-hongshi-breakthrough/ |

## Key specifications (PR; family level)

| Item | Value |
|---|---|
| Diagonal / resolution | 0.12", 640×480, ≈6,800 PPI (3.75 µm microLEDs) |
| Colour | Monochrome green |
| Brightness | Up to 8 million nits (vendor claim) |
| Process | 8-inch silicon-based GaN |

## G2 use (FW)

MSPI0 QSPI, 640×480 4 bpp. Brightness register E2 = `(in*250-451)/98+5`;
offsets in registers EF/F0 latched by D9=BF then D9=FF; status checks
BE == 0x84, reg 62 ∈ {0x77, 0x57}, D8 bit 0x20.

## Register map / SVD

None public.

## Relevance to decompilation

A second-source panel: both drivers are in the image and must both be
reconstructed.
