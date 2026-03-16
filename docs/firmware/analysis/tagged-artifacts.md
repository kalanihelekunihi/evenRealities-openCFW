# Tagged Firmware Artifacts

Generated local inventory for device-oriented firmware tags.

## Summary

- Generated at: `2026-03-05T22:14:03.498183+00:00`
- Materialized tagged tree: `True`
- Tagged root: `captures/firmware/tagged`
- G2-Case artifacts: `5`
- R1-Ring artifacts: `3`

## G2-Case

| Version | Tagged Path | Source Component | Source Package | SHA-256 |
|---|---|---|---|---|
| `2.0.1.14` | `captures/firmware/tagged/g2-case/2.0.1.14/firmware_box.bin` | `captures/firmware/versions/v2.0.1.14/extracted/firmware_box.bin` | `captures/firmware/versions/v2.0.1.14/09fe9c0df7b14385c023bc35a364b3a9.bin` | `7b3db020c80cd08fcdaaa2c21f7120dd56c5a74ab3704bd8b82db15aab73b188` |
| `2.0.3.20` | `captures/firmware/tagged/g2-case/2.0.3.20/firmware_box.bin` | `captures/firmware/versions/v2.0.3.20/extracted/firmware_box.bin` | `captures/firmware/versions/v2.0.3.20/57201a6e7cd6dadeee1bdb8f6ed98606.bin` | `fe0b3af4eb3c2b0a4981b9e1b09d622df3c6ad21944146e95dcef2bc598d5798` |
| `2.0.5.12` | `captures/firmware/tagged/g2-case/2.0.5.12/firmware_box.bin` | `captures/firmware/versions/v2.0.5.12/extracted/firmware_box.bin` | `captures/firmware/versions/v2.0.5.12/53486f03b825cb22d13e769187b46656.bin` | `fe0b3af4eb3c2b0a4981b9e1b09d622df3c6ad21944146e95dcef2bc598d5798` |
| `2.0.6.14` | `captures/firmware/tagged/g2-case/2.0.6.14/firmware_box.bin` | `captures/firmware/versions/v2.0.6.14/extracted/firmware_box.bin` | `captures/firmware/versions/v2.0.6.14/0c9f9ca58785547278a5103bc6ae7a09.bin` | `d290f2b6899e69288b2b07b2d52471f193a4bf065f3eefe664c5a89aeadecb52` |
| `2.0.7.16` | `captures/firmware/tagged/g2-case/2.0.7.16/firmware_box.bin` | `captures/firmware/versions/v2.0.7.16/extracted/firmware_box.bin` | `captures/firmware/versions/v2.0.7.16/650176717d1f30ef684e5f812500903c.bin` | `d290f2b6899e69288b2b07b2d52471f193a4bf065f3eefe664c5a89aeadecb52` |

## R1-Ring

| Tag | Kind | Version | Tagged Dir | Primary Binary | Source Bundle |
|---|---|---|---|---|---|
| `failsafe-bootloader` | `failsafe-bootloader` | `n/a` | `captures/firmware/tagged/r1-ring/failsafe-bootloader` | `captures/firmware/B210_ALWAY_BL_DFU_NO/bootloader.bin` | `captures/firmware/B210_ALWAY_BL_DFU_NO` |
| `bootloader-2.0.3.0004` | `bootloader` | `2.0.3.0004` | `captures/firmware/tagged/r1-ring/bootloader-2.0.3.0004` | `captures/firmware/B210_BL_DFU_NO_v2.0.3.0004/bootloader.bin` | `captures/firmware/B210_BL_DFU_NO_v2.0.3.0004` |
| `softdevice-2.0.3.0004` | `softdevice` | `2.0.3.0004` | `captures/firmware/tagged/r1-ring/softdevice-2.0.3.0004` | `captures/firmware/B210_SD_ONLY_NO_v2.0.3.0004/softdevice.bin` | `captures/firmware/B210_SD_ONLY_NO_v2.0.3.0004` |

## Notes

- `G2-Case` tags are extracted from the G2 EVENOTA package component `firmware/box.bin`.
- `R1-Ring` tags currently map to local Nordic DFU bundles already extracted from Even.app assets.
- This inventory does not make any claims about undiscovered remote endpoints; it only tags local artifacts.
