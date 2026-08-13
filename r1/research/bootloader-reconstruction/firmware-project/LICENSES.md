# Upstream licenses and redistribution boundary

The vendored dependency closure was copied unmodified from nRF5 SDK 17.1.0
`nRF5_SDK_17.1.0_ddde560.zip`, whose pinned SHA-256 is
`5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061`.

The relevant notices are retained inside `vendor/nrf5-sdk/`:

- `documentation/nRF5_Nordic_license.txt` for Nordic SDK source;
- `modules/nrfx/LICENSE` for nrfx;
- `external/nano-pb/LICENSE.txt` for nanopb;
- `external/nrf_cc310_bl/license.txt` for the supplied Arm CC310 BL headers/object library;
- `external/nrf_oberon/license.txt` for Nordic Oberon material; and
- `components/softdevice/s140/hex/s140_nrf52_7.2.0_licence-agreement.txt` for S140.

Individual upstream source files retain their original copyright and license headers. The complete
file inventory and SHA-256 ledger are `vendor/vendor-files.txt` and
`vendor/vendor-sha256.txt`. The Nordic-licensed material is restricted to use with Nordic
Semiconductor integrated circuits; this project targets the nRF52840.

Files outside `vendor/` are reconstruction material created for this repository or previously
recovered public product data. No ownership claim is made over the upstream implementations or the
captured retail firmware.

