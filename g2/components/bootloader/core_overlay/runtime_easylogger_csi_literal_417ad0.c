/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the authenticated G2 bootloader EasyLogger
 * ANSI color-output CSI-start literal. The first two bytes are the
 * well-known ANSI escape sequence ESC '[' (0x1B 0x5B) that opens every
 * EasyLogger terminal color-control sequence; the trailing two bytes are
 * compiler alignment padding to the next four-byte boundary.
 *
 * CANDIDATE, NOT YET PRODUCTION-ROUTED: this compiles byte-identical to the
 * authenticated stock bytes via apollo_overlay.compile_in_place_data_group
 * (verified interactively; see docs/research/
 * g2-bootloader-bl003-remaining-recon-4155e8-41a648.md), but
 * components/bootloader/core_overlay/build_component.py does not yet read
 * an `in_place_data` key the way the apollo_main core-component builder
 * does. It is not referenced by overlay.json and contributes zero bytes to
 * source-owned accounting until that wiring lands.
 */

const unsigned char open_cfw_bootloader_easylogger_csi_start_417ad0[4] = {
    0x1B, 0x5B, 0x00, 0x00,
};
