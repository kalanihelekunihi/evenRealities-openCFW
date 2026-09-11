/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the authenticated G2 bootloader SRAM address
 * literal retained between the CMSIS-RTOS2 event-flags set and wait entry
 * wrappers. Both neighboring wrappers load this constant as the address of
 * the shared runtime event-flags object they operate on; the object itself
 * lives in SRAM, outside this flash-resident literal.
 *
 * CANDIDATE, NOT YET PRODUCTION-ROUTED: this compiles byte-identical to the
 * authenticated stock word via apollo_overlay.compile_in_place_data_group
 * (verified interactively; see docs/research/
 * g2-bootloader-bl003-remaining-recon-4155e8-41a648.md), but
 * components/bootloader/core_overlay/build_component.py does not yet read
 * an `in_place_data` key the way the apollo_main core-component builder
 * does. It is not referenced by overlay.json and contributes zero bytes to
 * source-owned accounting until that wiring lands.
 */

const unsigned int open_cfw_bootloader_event_flags_object_addr_41658c =
    0x200270D4u;
