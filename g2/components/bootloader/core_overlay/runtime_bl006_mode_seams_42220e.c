/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the three literal seams between the exact
 * source-owned bitmap/mode bodies at 0x004220B2..0x004222F0.
 *
 * Each seam is a two-byte alignment filler followed by PC-relative literal
 * words consumed by neighboring in-place leaves (which keep their stock
 * literal addressing, so these pools stay live in the shipped image).
 * Every word below names its value, its consumers, and the reviewed
 * evidence for its meaning; see
 * docs/research/g2-bootloader-bl006-cluster-4220b2-422ad4-source-closure.md
 * for the full consumer table.
 */

typedef __UINT16_TYPE__ open_cfw_bl006_u16;
typedef __UINT32_TYPE__ open_cfw_bl006_u32;

/* Seam A at 0x0042220E: 2-byte fill + 4 words shared by the bitmap query
 * helpers and the mode service. */
struct __attribute__((packed)) open_cfw_bl006_seam_a {
    open_cfw_bl006_u16 align_fill; /* 0x0000: pool alignment after row6_enable */
    open_cfw_bl006_u32 bitmap_table_root; /* 0x20026E74: bitmap table root
        (bitmap-helpers closure; bitmap_any/test/count/update) */
    open_cfw_bl006_u32 mode_fallback_table; /* 0x00433F08: mode fallback
        template table pointer; target holds {0x0025B800,0,0} (mode-service
        closure, host local[3]); target bytes stay BL-012 retained */
    open_cfw_bl006_u32 mode_special_instance; /* 48000000: fixed mode instance
        OPEN_CFW_MODE_SPECIAL (runtime_mode_service_4216d4.c; mode_service) */
    open_cfw_bl006_u32 mode_controller_seam; /* 0x2000007C: controller seam
        cell (mode-service closure; host controller); read by mode_service,
        dual_mode_service, bitmap_client_service, row-one set, mode enables,
        and the mode copy helper */
};

__attribute__((used, section(".rodata.bl006_seam_42220e")))
const struct open_cfw_bl006_seam_a open_cfw_bootloader_bl006_seam_42220e = {
    0x0000u, 0x20026E74u, 0x00433F08u, 48000000u, 0x2000007Cu
};

/* Seam B at 0x0042228E: 2-byte fill + 4 words shared by the mode service,
 * mode-zero cleanup, and row-four enable paths. */
struct __attribute__((packed)) open_cfw_bl006_seam_b {
    open_cfw_bl006_u16 align_fill; /* 0x0000: pool alignment after row6_disable */
    open_cfw_bl006_u32 mode_current_instance; /* 0x20027030: mode
        current-instance word (host current; compared against 0 and the
        special instance by mode_service, word-compared by row4_enable) */
    open_cfw_bl006_u32 mode_fallback_base; /* 0x20026FEC: mode fallback
        word-array base (host fallback[3]); [base] is applied by
        mode_service and row4_enable */
    open_cfw_bl006_u32 mode0_polled_byte; /* 0x2002719C: mode-zero polled
        byte (mode0-disable closure; host aux flag cleared on the mode
        idle path); polled by mode0 cleanup and row4_enable, cleared by
        mode_service */
    open_cfw_bl006_u32 mode0_state_pointer; /* 0x20027044: mode-zero state
        pointer (mode0-disable closure; host aux word cleared on the mode
        idle path); read by mode_service, mode0 cleanup, row4_enable */
};

__attribute__((used, section(".rodata.bl006_seam_42228e")))
const struct open_cfw_bl006_seam_b open_cfw_bootloader_bl006_seam_42228e = {
    0x0000u, 0x20027030u, 0x20026FECu, 0x2002719Cu, 0x20027044u
};

/* Seam C at 0x004222D2: 2-byte fill + 7 words shared by the dual-mode,
 * row-four, and row-five services. */
struct __attribute__((packed)) open_cfw_bl006_seam_c {
    open_cfw_bl006_u16 align_fill; /* 0x0000: pool alignment after mode_dispatch */
    open_cfw_bl006_u32 shared_instance_compare; /* 0x20000550:
        instance-comparison cell: word-compared against the instance
        argument on the mode busy path, byte-polled by row4_enable.
        No host-variable mapping is established; see the audit. */
    open_cfw_bl006_u32 dual_accepted_instance_hi; /* 250000000: accepted
        dual-mode instance (dual-mode closure) */
    open_cfw_bl006_u32 dual_current_instance; /* 0x20027034: dual-mode
        current-instance publication (dual-mode closure); read by dual,
        row5_enable, row5_disable */
    open_cfw_bl006_u32 dual_query_template; /* 0x00433F14: dual query
        template pointer; target holds {0x00020000,0x000C49BA,0}
        (dual-mode closure); target bytes stay BL-012 retained */
    open_cfw_bl006_u32 dual_accepted_instance_lo; /* 196608000: accepted
        dual-mode instance (dual-mode closure) */
    open_cfw_bl006_u32 dual_config_publication; /* 0x20026FF8: dual-mode
        12-byte configuration publication base (dual-mode closure);
        first byte also polled by row5_enable */
    open_cfw_bl006_u32 dual_readiness_byte; /* 0x20000551: dual-mode
        readiness byte (dual-mode closure); polled by row5_enable */
};

__attribute__((used, section(".rodata.bl006_seam_4222d2")))
const struct open_cfw_bl006_seam_c open_cfw_bootloader_bl006_seam_4222d2 = {
    0x0000u, 0x20000550u, 250000000u, 0x20027034u, 0x00433F14u,
    196608000u, 0x20026FF8u, 0x20000551u
};
