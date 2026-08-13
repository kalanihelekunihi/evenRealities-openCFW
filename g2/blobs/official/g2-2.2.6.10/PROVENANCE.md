# Official G2 2.2.6.10 blob provenance

Source bundle:

- local mirror path:
  `firmware/ota/2026-07-22/g2-2.2.6.10-e28738432d7b612d625331b00383149b.bin`
- version: `s200_v2.2.6.10`
- build date/time: `2026-07-06 21:39:36`
- size: 4,301,227 bytes
- SHA-256:
  `f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa`

The six files in this directory are the exact payload bytes after removing
the outer EVENOTA TOC and each 128-byte component header. They were copied
from the validated extraction under
`firmware/analysis/g2-2.2.6.10/`.

| Blob | Size | SHA-256 |
|---|---:|---|
| `firmware_codec.bin` | 326,092 | `b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0` |
| `firmware_ble_em9305.bin` | 211,948 | `91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9` |
| `firmware_touch.bin` | 34,464 | `0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d` |
| `firmware_box.bin` | 55,784 | `36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374` |
| `ota_s200_bootloader.bin` | 148,599 | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` |
| `ota_s200_firmware_ota.bin` | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |

The blobs are retained only as opaque compatibility inputs while equivalent
source implementations are developed. They remain vendor-proprietary; this
provenance record does not grant redistribution rights.

