# HAL request routing integration (2026-10-06)

The shared request dispatcher at stock `0x4251c0` now routes request 30 to `opencfw_hal_mspi_control_transaction_request(handle, request, config)` and request 34 to `opencfw_hal_mspi_control_request34(handle, config)`. Other recovered cases retain their existing provider routes. An unmatched request in this bounded helper returns status 6; the outer dispatcher validates its request domain. The obsolete `opencfw_hal_mspi_control_unrecovered_request` declaration and fallback call are removed.

The five coupled worker ELF fixtures were rebuilt with both new handlers linked. Each differential runs the pinned stock dispatcher against synthetic RAM/MSPI MMIO and source ELF; no hardware access is involved. Results:

- `control-request-state/result.json`: PASS, 172 cases, 1404 distinct stock instruction bytes, ELF SHA-256 `ac84c506347405a2bb7718e480fca6e0a64208ce3514477d0117aace674c07da`, receipt SHA-256 `5f0a17ee198d02eebad9478fc507c8a77b0e06563840793d75b2d31c77f914b0`.
- `control-request-extension/result.json`: PASS, 20 cases, 706 distinct stock instruction bytes, ELF SHA-256 `dc9f4301c58a1fce62274ba62eeb8560eccf1789e5e2c466da5e5a2da3e97334`, receipt SHA-256 `6dd10bb017f971f45549454a1c3332099415da5c97e86159739f75828cfeb66d`.
- `control-request-transactions/result.json`: PASS, 33 cases, 1172 distinct stock instruction bytes, ELF SHA-256 `801167f2df09a7c2916b7e9123a1688388002ff2d67ce737c329d0c82f33a921`, receipt SHA-256 `34f867e778ac4b7e292b0e2b1d6cf02252cdab05350307924d90a510069c7cca`.
- `control-request34/result.json`: PASS, 19 cases, 1050 distinct stock instruction bytes, ELF SHA-256 `67f08decb765b3acdceae505726f418a8bf323b08d0c1a061a21402f75c5a0df`, receipt SHA-256 `66799641e1c0de78326fd39051f701da83846f5cb1206656f8341413ff673b5a`.
- `control-remaining/result.json`: PASS, 972 cases, 2660 distinct stock instruction bytes, ELF SHA-256 `29e7671bbb830524ff13d1dfcfd4c47553d489983130d338151e3ceb96c01fdf`, receipt SHA-256 `2e2e14e3c0c6a65951042bbf61973413786be40e748a63d8c8b8dbb401305eb8`.
Shared integration image exercised after the dedicated linked-symbol clock boundary was added:

- `control-request-transactions/shared-source-image-b451c420.json`: PASS, 33 cases, 1172 original bytes, receipt SHA-256 `30db72a23f4377ab746b63b701678abce40e21231b2713ee4f5bfc640c41e039`. The source ELF SHA-256 is `b451c42007ed87152ecbfb4ba6911d737675062a9508f7b83d964acff556be0c`.
- `control-request34/shared-source-image-b451c420.json`: PASS, 19 cases, 1050 original bytes, receipt SHA-256 `dd0d6e4bc985fdf9e9048c434debbc722ed17b450f26d1f349698c63db986d62`. The source ELF SHA-256 is `b451c42007ed87152ecbfb4ba6911d737675062a9508f7b83d964acff556be0c`.

The combined ELF symbol `clock_request` resolves at Thumb address `0x12531`; fixtures derive the synthetic provider hook from this linked symbol (masking the Thumb bit), while the original side remains intercepted at internal firmware address `0x4222f0`. The hook returns the selected synthetic clock status and does not execute the combined clock implementation. Queue descriptors, allocator/queue, CQ and control handlers execute from the shared ELF; hardware MMIO remains modeled.


Latest pinned integration snapshot `3388449d9ec79c9719ebafed8553b847355a83013b7abfc932aa1204703e0ec4` was rechecked after adding its 64-byte initializer configuration arrays. Separate receipts preserve the earlier `b451c420` snapshot results:

- `control-request-transactions/shared-source-image-3388449d.json`: PASS, 33 cases / 1172 original bytes; ELF SHA-256 `3388449d9ec79c9719ebafed8553b847355a83013b7abfc932aa1204703e0ec4`, receipt SHA-256 `5e019b63d01714c64c45dee35e2df787c900b286ca75e018b915767bd78fb6ec`.
- `control-request34/shared-source-image-3388449d.json`: PASS, 19 cases / 1050 original bytes; ELF SHA-256 `3388449d9ec79c9719ebafed8553b847355a83013b7abfc932aa1204703e0ec4`, receipt SHA-256 `93d6785fd5f14fb1e8ed9dbddf39300395b1b140c8cc8b59d2116b3bdf46f7db`.

The stock clock interception address `0x4222f0` is inside the locked firmware image, not ROM. The source-side synthetic hook is derived from linked `clock_request` (`0x12531`).


Aligned integrated candidate snapshot `4083142fce6a0a8ecbc5d3d1a9a224ee475479676d2aa3e8b8bd402ee9144007` recheck:

- `control-request-transactions/shared-source-image-4083142f.json`: PASS, 33 cases / 1172 original bytes; ELF SHA-256 `4083142fce6a0a8ecbc5d3d1a9a224ee475479676d2aa3e8b8bd402ee9144007`, receipt SHA-256 `50e42fa9dea5af962463c2262b39a84d515213c6d968c7a8b38a131157ab5d76`.
- `control-request34/shared-source-image-4083142f.json`: PASS, 19 cases / 1050 original bytes; ELF SHA-256 `4083142fce6a0a8ecbc5d3d1a9a224ee475479676d2aa3e8b8bd402ee9144007`, receipt SHA-256 `b526367f3a0a33a33b001b556f5b127aeb69d82f542ff0b903b8013b2a699c2d`.

The stock callback address `0x4222f0` is internal to the locked bootloader image; the synthetic source-side clock cut is derived from the ELF symbol `clock_request`.


Final DCE candidate retake (`dceae3b56c3ef4b0572f4cd499230ca8f5eb20419cf1c4a0910d05d607389bee`):

- `control-request-transactions/shared-source-image-dceae3.json`: PASS, 33 cases / 1172 original bytes; final ELF SHA-256 `dceae3b56c3ef4b0572f4cd499230ca8f5eb20419cf1c4a0910d05d607389bee`, receipt SHA-256 `f98ad069cc453cd0238b7c9c1470c0d68a44883584d38730209f4164f95f6fea`.
- `control-request34/shared-source-image-dceae3.json`: PASS, 19 cases / 1050 original bytes; final ELF SHA-256 `dceae3b56c3ef4b0572f4cd499230ca8f5eb20419cf1c4a0910d05d607389bee`, receipt SHA-256 `93cfd633b7938c12ed9080993f927954639650811990e67f8fec8b1ad473b7bf`.

Clock uses the already documented source-symbol-derived synthetic boundary. These receipts replace earlier snapshots for final dispatcher binding evidence; they do not overwrite prior receipts.


Frozen 4598 candidate retake after native kernel-state binding (`4598040563d8f41b2fc71d430114b6b8564198b439e7225e9729d2f1c93acc2e`):

- `control-request-transactions/shared-source-image-459804.json`: PASS, 33 cases / 1172 original bytes; ELF SHA-256 `4598040563d8f41b2fc71d430114b6b8564198b439e7225e9729d2f1c93acc2e`, receipt SHA-256 `41663fd5d874665228b371f704bc3dff1a31b6c2b902d2b2fb2d53795eece47d`.
- `control-request34/shared-source-image-459804.json`: PASS, 19 cases / 1050 original bytes; ELF SHA-256 `4598040563d8f41b2fc71d430114b6b8564198b439e7225e9729d2f1c93acc2e`, receipt SHA-256 `f2a8d171380ed37a4c6498e0d8a132f783d70124ada17cb301b0fc786ea2f255`.

The lifecycle comparison against the same ELF is saved separately at `kernel-state-candidate/result-459804.json`; it passes 216 cases / 224 original bytes and reports the same ELF SHA-256.
