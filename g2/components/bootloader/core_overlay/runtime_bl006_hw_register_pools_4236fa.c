/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the hardware register/status/clock pools at
 * 0x004236FA..0x00423700, 0x00423764..0x0042377C, and
 * 0x0042382C..0x00423864.
 *
 * These words sit between exact source-owned in-place leaves (register
 * services, identity words, service dispatcher, bounded memory-exchange
 * helpers), which keep their stock PC-relative literal addressing, so
 * the pools stay live in the shipped image. Every word below names its
 * value, its live consumers (loader PCs verified by bounded Capstone
 * decode of the routed spans; zero consumers live in entry-redirect
 * stock spans), and its meaning from the already-reviewed consumer
 * host models; see
 * docs/research/g2-bootloader-bl006-cluster-4233e0-4251c0-source-closure.md
 * for the full consumer table.
 */

typedef __UINT16_TYPE__ open_cfw_bl006_u16;
typedef __UINT32_TYPE__ open_cfw_bl006_u32;

/* Pool at 0x004236FA: 2-byte alignment fill plus the 3 MHz clock
 * reference. The clock divider's mode-4 path (0x00422EB0) loads the
 * reference word; the stock compiler placed it here because the
 * mode-6..3 references already filled the later pool. Host model
 * `references[4]` (30/3000000 entries read `references[mode]`). */
struct __attribute__((packed)) open_cfw_bl006_pool_4236fa {
    open_cfw_bl006_u16 align_fill; /* 0x0000: pool alignment */
    open_cfw_bl006_u32 reference_3mhz; /* 3000000: mode-4 reference Hz */
};

__attribute__((used, section(".rodata.bl006_pool_4236fa")))
const struct open_cfw_bl006_pool_4236fa open_cfw_bootloader_bl006_pool_4236fa = {
    0x0000u, 3000000u
};

/* Pool at 0x00423764: register-bank base plus the per-instance status
 * fault codes. The status mapper (0x00422D8E..0x00422DC0) returns one
 * code per set status bit; host model
 * `open_cfw_bootloader_hw_status_map_422d7e`. */
struct __attribute__((packed)) open_cfw_bl006_pool_423764 {
    open_cfw_bl006_u32 register_bank_base; /* 0x40039000: peripheral
        register-bank base, 0x1000 stride. Read by the FIFO pump
        (0x004233A0), FIFO read (0x004232EC), FIFO write (0x00423324),
        register clear (0x00422D4E), register OR (0x004236E6),
        register query (0x0042374A/0x00423754), register write
        (0x00423718), and shutdown (0x00422FE8). */
    open_cfw_bl006_u32 status_bit6; /* 0x08000006: bit-6 fault code */
    open_cfw_bl006_u32 status_bit7; /* 0x08000007: bit-7 fault code */
    open_cfw_bl006_u32 status_bit8; /* 0x08000008: bit-8 fault code */
    open_cfw_bl006_u32 status_bit9; /* 0x08000009: bit-9 fault code */
    open_cfw_bl006_u32 status_bit10; /* 0x0800000A: bit-10 fault code */
};

__attribute__((used, section(".rodata.bl006_pool_423764")))
const struct open_cfw_bl006_pool_423764 open_cfw_bootloader_bl006_pool_423764 = {
    0x40039000u, 0x08000006u, 0x08000007u, 0x08000008u, 0x08000009u,
    0x0800000Au
};

/* Pool at 0x0042382C: status bit-12 code, descriptor magic, clock
 * references and statuses, latch statuses, shutdown delay reference,
 * snapshot status, and the service-dispatch bank base. */
struct __attribute__((packed)) open_cfw_bl006_pool_42382c {
    open_cfw_bl006_u32 status_bit12; /* 0x0800000B: bit-12 fault code
        (status mapper, 0x00422DC0). */
    open_cfw_bl006_u32 descriptor_magic; /* 0x01EA9E06: descriptor-header
        magic, low 25 bits. Guarded by descriptor init (0x00422DD6),
        mode dispatch (0x004233F4), register OR (0x004236DC),
        register query (0x0042373A), register write (0x0042370E),
        and service dispatch (0x0042378E); host models spell it
        `(x & 0x01FFFFFFU) != 0x01EA9E06U`. */
    open_cfw_bl006_u32 reference_max; /* 49152000: mode-6 reference Hz
        (clock divider, 0x00422E58); host `references[6]`. */
    open_cfw_bl006_u32 divider_error; /* 0x08000003: divider
        zero/overflow status (clock divider, 0x00422E92); host
        `divisor == 0` / `integer == 0` returns. */
    open_cfw_bl006_u32 reference_48mhz; /* 48000000: mode-5 reference Hz
        (clock divider, 0x00422E98); host `references[5]`. */
    open_cfw_bl006_u32 reference_24mhz; /* 24000000: mode-1 reference Hz
        (clock divider, 0x00422E9E); host `references[1]`. */
    open_cfw_bl006_u32 reference_12mhz; /* 12000000: mode-2 reference Hz
        (clock divider, 0x00422EA4); host `references[2]`. */
    open_cfw_bl006_u32 reference_6mhz; /* 6000000: mode-3 reference Hz
        (clock divider, 0x00422EAA); host `references[3]`. */
    open_cfw_bl006_u32 divider_idle; /* 0x08000002: divider idle-mode
        status (clock divider, 0x00422EBC); host
        `mode == 0 || mode == 7` return. */
    open_cfw_bl006_u32 latch_status; /* 0x08000004: configuration-latch
        status (config latch, 0x00422F3E). */
    open_cfw_bl006_u32 latch_secondary_status; /* 0x08000005:
        secondary-latch status (config latch secondary, 0x00422F94). */
    open_cfw_bl006_u32 shutdown_hz; /* 10000000: shutdown delay
        reference Hz (shutdown, 0x0042303A); host model
        `host_delay(10000000U / divisor + 1)`. */
    open_cfw_bl006_u32 snapshot_status; /* 0x08000001: FIFO-snapshot
        status (FIFO snapshot, 0x00423380). */
    open_cfw_bl006_u32 dispatch_bank_base; /* 0x40039000: peripheral
        register-bank base for the service dispatcher (0x004237AE). */
};

__attribute__((used, section(".rodata.bl006_pool_42382c")))
const struct open_cfw_bl006_pool_42382c open_cfw_bootloader_bl006_pool_42382c = {
    0x0800000Bu, 0x01EA9E06u, 49152000u, 0x08000003u, 48000000u,
    24000000u, 12000000u, 6000000u, 0x08000002u, 0x08000004u,
    0x08000005u, 10000000u, 0x08000001u, 0x40039000u
};
