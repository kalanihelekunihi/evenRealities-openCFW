/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the hardware-service instance pools at
 * 0x004233E0..0x004233E8 and 0x00423430..0x00423444.
 *
 * Both pools sit between exact source-owned in-place leaves (the FIFO
 * adapters, mode dispatcher, and wait wrappers keep their stock
 * PC-relative literal addressing, so these words stay live in the
 * shipped image). Every word below names its value, its live
 * consumers (loader PCs verified by bounded Capstone decode of the
 * routed spans; zero consumers live in entry-redirect stock spans),
 * and its meaning from the already-reviewed consumer host models; see
 * docs/research/g2-bootloader-bl006-cluster-4233e0-4251c0-source-closure.md
 * for the full consumer table.
 */

typedef __UINT32_TYPE__ open_cfw_bl006_u32;

/* Pool at 0x004233E0: instance-header match word plus the
 * instance-descriptor table base. */
struct __attribute__((packed)) open_cfw_bl006_pool_4233e0 {
    open_cfw_bl006_u32 header_match; /* 0x01EA9E06: instance-header magic,
        low 25 bits. Compared (after BIC against 0xFE000000) by the
        hardware initializer (0x0042309E), the four-instance initializer
        (0x00422AF4), and the instance service (0x0042BB8); host models
        spell it `(header & ~0xFE000000U) == 0x01EA9E06U`. */
    open_cfw_bl006_u32 descriptor_base; /* 0x20024400: instance-descriptor
        table base. The four-instance initializer (0x00422B24 region
        load) indexes 0x11C-byte entries from it; host model
        `open_cfw_hw_host_instances[index]`. */
};

__attribute__((used, section(".rodata.bl006_pool_4233e0")))
const struct open_cfw_bl006_pool_4233e0 open_cfw_bootloader_bl006_pool_4233e0 = {
    0x01EA9E06u, 0x20024400u
};

/* Pool at 0x00423430: fresh-header word, requested-frequency
 * threshold, chip-revision and global-control registers, and the
 * peripheral register-bank base. */
struct __attribute__((packed)) open_cfw_bl006_pool_423430 {
    open_cfw_bl006_u32 header_fresh; /* 0x00EA9E06: fresh-header low word,
        ORed into the preserved top byte when an instance is claimed
        (four-instance initializer, 0x00422B24); host model
        `(header & 0xFF000000U) | 0x00EA9E06U`. */
    open_cfw_bl006_u32 request_threshold; /* 0x0016E361 (1500001):
        requested-frequency threshold selecting the high-speed init
        path (hardware initializer 0x004230F4, instance service
        0x00422BF8/0x00422CC8); host model
        `requested >= 0x0016E361U`. */
    open_cfw_bl006_u32 chip_revision_reg; /* 0x4002000C: chip-revision
        register. Low byte compared against 0x21/0x22 by the hardware
        initializer (0x004230D0/0x004230FA/0x00423132) and the instance
        service (0x00422C00/0x00422CD0); host model
        `open_cfw_hwinit_host_chip_revision`. */
    open_cfw_bl006_u32 global_control_reg; /* 0x400201B0: global-control
        register. Bit `0x00400000 << index` set/cleared by the hardware
        initializer (0x00423106/0x0042313E) and the instance service
        (0x00422C0E/0x00422CDE); host model
        `open_cfw_hwinit_host_global_control`. */
    open_cfw_bl006_u32 register_bank_base; /* 0x40039000: peripheral
        register-bank base, 0x1000 stride per instance. Read by the
        clock divider (0x00422E32), the hardware initializer
        (0x004230AA), the instance service (0x00422C2C/0x00422C7E/
        0x00422D08), the register clear leaf (0x00422D22), and the
        status mapper (0x00422D7E); host models
        `open_cfw_hw*_host_registers[index]`. */
};

__attribute__((used, section(".rodata.bl006_pool_423430")))
const struct open_cfw_bl006_pool_423430 open_cfw_bootloader_bl006_pool_423430 = {
    0x00EA9E06u, 0x0016E361u, 0x4002000Cu, 0x400201B0u, 0x40039000u
};
