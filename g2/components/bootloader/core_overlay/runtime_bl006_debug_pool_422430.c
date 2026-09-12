/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the debug-service literal pool (0x00422430),
 * the debug-trace literal pool (0x00422574), and the constraint-handler
 * message island (0x004225AC).
 *
 * All three are consumed by neighboring in-place leaves through stock
 * PC-relative addressing, so they stay live in the shipped image. Every
 * field below names its value, its consumers, and the reviewed evidence
 * for its meaning; see
 * docs/research/g2-bootloader-bl006-cluster-4220b2-422ad4-source-closure.md
 * for the full consumer table.
 */

typedef __UINT32_TYPE__ open_cfw_bl006_u32;

/* Pool D at 0x00422430: 14 words published and polled by the bitmap,
 * mode, row-four, row-five, and row-six client services. */
struct __attribute__((packed)) open_cfw_bl006_debug_pool {
    open_cfw_bl006_u32 bitmap_config_publication; /* 0x20027004: 12-byte
        configuration publication (bitmap-clients closure); row6_enable
        and row6_disable read its first byte for selector ordering */
    open_cfw_bl006_u32 bitmap_current_instance; /* 0x20027038: current
        instance (bitmap-clients closure) */
    open_cfw_bl006_u32 bitmap_readiness_byte; /* 0x2002719A: readiness
        byte (bitmap-clients closure); row6_enable gates mode brings on it
        (host ready) */
    open_cfw_bl006_u32 mode1_enable_control_word; /* 0x0043414C: mode-one
        enable control word base; the enable leaf overwrites its low
        nibble with 0xA at runtime (host enable_word; request 15) */
    open_cfw_bl006_u32 mode1_disable_control_word; /* 0x00434150: mode-one
        disable control word (host disable_word; request 15) */
    open_cfw_bl006_u32 mode_active_byte; /* 0x2002719B: mode active byte
        (mode1 closure; shared by the mode-zero leaves) */
    open_cfw_bl006_u32 mode_state_word; /* 0x20027040: mode state
        word/pointer (mode1 closure; shared by the mode-zero leaves) */
    open_cfw_bl006_u32 mode0_completion_byte; /* 0x2002719E: mode-zero
        completion byte (mode0-disable closure); set by row4_enable */
    open_cfw_bl006_u32 row4_active_byte; /* 0x2002719D: row-four active
        byte (row4-disable closure); polled by row5_enable */
    open_cfw_bl006_u32 row4_state_pointer; /* 0x20027048: row-four state
        pointer (row4-disable closure); double-dereferenced by row5_enable */
    open_cfw_bl006_u32 row5_active_byte; /* 0x2002719F: row-five active
        byte (row5 closure "active/state cells"); set by row5_enable,
        cleared by row5_disable through the dual switch */
    open_cfw_bl006_u32 row6_pending_byte; /* 0x200271A0: row-six pending
        byte (host pending); set by row6_enable, cleared by row6_disable */
    open_cfw_bl006_u32 row6_service_handle; /* 0x2002703C: row-six
        retained service handle word (host handle); created, configured,
        started, and destroyed by the row-six leaves */
    open_cfw_bl006_u32 controller_seam_copy; /* 0x2000007C: the same
        controller seam cell as seam A (mode routes copy helper) */
};

__attribute__((used, section(".rodata.bl006_pool_422430")))
const struct open_cfw_bl006_debug_pool open_cfw_bootloader_bl006_pool_422430 = {
    0x20027004u, 0x20027038u, 0x2002719Au, 0x0043414Cu, 0x00434150u,
    0x2002719Bu, 0x20027040u, 0x2002719Eu, 0x2002719Du, 0x20027048u,
    0x2002719Fu, 0x200271A0u, 0x2002703Cu, 0x2000007Cu
};

/* Pool E at 0x00422574: reserved zero word + 6 words owned by the
 * debug-disable, debug-power, and trace-disable leaves. */
struct __attribute__((packed)) open_cfw_bl006_trace_pool {
    open_cfw_bl006_u32 reserved_zero; /* 0x00000000: no routed consumer.
        The whole-image scan finds no PC-relative load targeting it in
        any in-place or entry-redirect stock span, and the +/-4KB window
        holds no retained code, so no shipped instruction can read it.
        Preserved as an authenticated zero pad. */
    open_cfw_bl006_u32 debug_enable_count; /* 0x200271A1: debug user
        reference count (host enable_count); decremented by debug_disable */
    open_cfw_bl006_u32 debug_control_register; /* 0x40020250: debug
        control register (host dbgctrl); debug_disable clears its low
        four enable/clock bits for the last user */
    open_cfw_bl006_u32 debug_power_count; /* 0x200271A2: debug power
        reference count (host power_count) */
    open_cfw_bl006_u32 debug_power_entry_state; /* 0x200271A4: power
        entry state (host power_entry_state) */
    open_cfw_bl006_u32 debug_trace_count; /* 0x200271A3: trace
        reference count (host trace_count) */
    open_cfw_bl006_u32 debug_demcr; /* 0xE000EDFC: architectural DCB
        DEMCR (host demcr); trace_disable clears TRCENA (bit 24) and
        polls the register */
};

__attribute__((used, section(".rodata.bl006_pool_422574")))
const struct open_cfw_bl006_trace_pool open_cfw_bootloader_bl006_pool_422574 = {
    0x00000000u, 0x200271A1u, 0x40020250u, 0x200271A2u, 0x200271A4u,
    0x200271A3u, 0xE000EDFCu
};

/* Island F at 0x004225AC: handler cell + IAR CLIB default message,
 * consumed by the in-place constraint dispatcher. */
struct __attribute__((packed)) open_cfw_bl006_constraint_island {
    open_cfw_bl006_u32 constraint_handler_cell; /* 0x20027190:
        registered C11 constraint-handler pointer cell
        (constraint-memchr closure); a null entry selects the retained
        default handler at 0x00417C28, otherwise the handler receives
        (message, NULL, 0x22) */
    char constraint_bad_message[32]; /* IAR CLIB default
        constraint-violation message (host bad_message) */
};

__attribute__((used, section(".rodata.bl006_island_4225ac")))
const struct open_cfw_bl006_constraint_island
open_cfw_bootloader_bl006_island_4225ac = {
    0x20027190u, "constraint handler: bad message"
};
