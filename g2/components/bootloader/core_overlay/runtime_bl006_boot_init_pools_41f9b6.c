/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the boot-initialization literal pools at
 * 0x0041F9B6..0x0041F9CC, 0x0041F9EE, 0x0041FA40..0x0041FA50,
 * 0x0041FAD0..0x0041FADC, 0x0041FCF6..0x0041FD70, and
 * 0x0041FDA8..0x0041FDC0.
 *
 * Every word below names its value, the stock loader PCs that read it
 * (verified by bounded Capstone decode of the authenticated image; the
 * loaders live in entry-redirect stock spans, so the relocated leaves
 * carry their own copies and these pools are NOT address-live in the
 * final image), and its meaning from the already-reviewed consumer
 * host models; see
 * docs/research/g2-bootloader-bl006-cluster-41f9b6-41fdc0-source-closure.md
 * for the full loader table. The trailing island words at
 * 0x0041F9CC..0x0041F9D8 point into unidentified retained globals and
 * stay retained for the owning item.
 */

typedef __UINT16_TYPE__ open_cfw_bl006_u16;
typedef __UINT32_TYPE__ open_cfw_bl006_u32;

/* Pool at 0x0041F9B6 (first 22 bytes of the island): 2-byte fill plus
 * four system-control-space register bases and the EasyLogger
 * transport-table address. F9B8 is word-aligned. No stock loader reads
 * the four SCS words (orphaned literals); F9C8 is loaded by the
 * EasyLogger channel-write body (0x0041F93A). */
struct __attribute__((packed)) open_cfw_bl006_pool_41f9b6 {
    open_cfw_bl006_u16 align_fill; /* 0x0000: pool alignment */
    open_cfw_bl006_u32 nvic_iser0; /* 0xE000E100: NVIC interrupt-set-enable
        register 0 (reviewed irq_services host OPEN_CFW_NVIC_ISER) */
    open_cfw_bl006_u32 nvic_icpr0; /* 0xE000E280: architectural NVIC
        interrupt-clear-pending register 0; no reviewed consumer names
        it and no stock loader reads it -- reproduced as a named layout
        constant, not as claimed data */
    open_cfw_bl006_u32 nvic_ipr0; /* 0xE000E400: NVIC interrupt-priority
        register 0 (reviewed irq_services host OPEN_CFW_NVIC_IPR) */
    open_cfw_bl006_u32 scb_shpr2; /* 0xE000ED18: System Control Block
        system-handler-priority register 2 (reviewed irq_services host
        OPEN_CFW_SCB_SHP) */
    open_cfw_bl006_u32 elog_transport_table; /* 0x20000454: EasyLogger
        transport table base (reviewed transport host
        OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_TABLE_ADDRESS; stock loader
        0x0041F93A) */
};

__attribute__((used, section(".rodata.bl006_pool_41f9b6")))
const struct open_cfw_bl006_pool_41f9b6 open_cfw_bootloader_bl006_pool_41f9b6 = {
    0x0000u, 0xE000E100u, 0xE000E280u, 0xE000E400u, 0xE000ED18u, 0x20000454u
};

/* Word at 0x0041F9EE: zero alignment halfword padding the raw boot
 * delay wrapper (ends 0x0041F9EE) so the initializer priority
 * comparator entry at 0x0041F9F0 stays aligned. */
__attribute__((used, section(".rodata.bl006_align_41f9ee")))
const open_cfw_bl006_u16 open_cfw_bootloader_bl006_align_41f9ee = 0x0000u;

/* Pool at 0x0041FA40: initializer-table bounds, scratch, and
 * comparator entry consumed by the run-initializers service
 * (stock loaders 0x0041F9FA/0x0041F9FC/0x0041FA10/0x0041FA1A). */
struct __attribute__((packed)) open_cfw_bl006_pool_41fa40 {
    open_cfw_bl006_u32 initializer_begin; /* 0x00433440: table begin
        (reviewed boot-services host
        OPEN_CFW_BOOT_SERVICE_INITIALIZER_BEGIN; loader 0x0041F9FA) */
    open_cfw_bl006_u32 initializer_end; /* 0x00433460: table end
        (reviewed host OPEN_CFW_BOOT_SERVICE_INITIALIZER_END; loader
        0x0041F9FC) */
    open_cfw_bl006_u32 initializer_scratch; /* 0x20022E00: sort scratch
        cell (reviewed host OPEN_CFW_BOOT_SERVICE_INITIALIZER_SCRATCH;
        loader 0x0041FA10) */
    open_cfw_bl006_u32 comparator_thumb; /* 0x0041F9F1: priority
        comparator Thumb entry (reviewed host
        OPEN_CFW_BOOT_SERVICE_COMPARATOR_THUMB; loader 0x0041FA1A) */
};

__attribute__((used, section(".rodata.bl006_pool_41fa40")))
const struct open_cfw_bl006_pool_41fa40 open_cfw_bootloader_bl006_pool_41fa40 = {
    0x00433440u, 0x00433460u, 0x20022E00u, 0x0041F9F1u
};

/* Pool at 0x0041FAD0: guard byte cell, platform-configuration base,
 * and pin-configuration word consumed by the guarded teardown
 * (stock loaders 0x0041FA9A/0x0041FABE) and the boot-platform setup
 * entry (stock loader 0x0041FA70). */
struct __attribute__((packed)) open_cfw_bl006_pool_41fad0 {
    open_cfw_bl006_u32 teardown_guard; /* 0x20027198: teardown guard
        cell (reviewed teardown host OPEN_CFW_TEARDOWN_GUARD; loader
        0x0041FA9A) */
    open_cfw_bl006_u32 platform_config; /* 0x00433A9C: 20-byte platform
        configuration base (reviewed platform host
        OPEN_CFW_PLATFORM_CONFIG; loader 0x0041FA70) */
    open_cfw_bl006_u32 pin_config_word; /* 0x00434154: pin-configuration
        word (reviewed teardown host OPEN_CFW_TEARDOWN_PIN_CONFIG;
        loader 0x0041FABE) */
};

__attribute__((used, section(".rodata.bl006_pool_41fad0")))
const struct open_cfw_bl006_pool_41fad0 open_cfw_bootloader_bl006_pool_41fad0 = {
    0x20027198u, 0x00433A9Cu, 0x00434154u
};

/* Pool at 0x0041FCF6: 2-byte fill plus the 30 pin-configuration SRAM
 * addresses consumed by the two-bank pin-group dispatcher (stock
 * loaders listed per slot). Each value is OPEN_CFW_PIN_CONFIG_BASE
 * (0x20000000) plus the offset named in the reviewed dispatcher;
 * the (pin, offset) pair after each field is the stock call site
 * that loads the slot, and every pair matches the reviewed
 * pin-group bank/subtype paths exactly. */
struct __attribute__((packed)) open_cfw_bl006_pool_41fcf6 {
    open_cfw_bl006_u16 align_fill; /* 0x0000: pool alignment */
    open_cfw_bl006_u32 cfg_10; /* 0x20000010: bank-zero pair pin 0x43
        (loader 0x0041FBE0) */
    open_cfw_bl006_u32 cfg_0c; /* 0x2000000C: bank-zero pair pin 0x42
        (loader 0x0041FBD4) */
    open_cfw_bl006_u32 cfg_08; /* 0x20000008: bank-zero common pin 0x41
        (loader 0x0041FC04) */
    open_cfw_bl006_u32 cfg_04; /* 0x20000004: bank-zero common pin 0x40
        (loader 0x0041FBF8) */
    open_cfw_bl006_u32 cfg_00; /* 0x20000000: bank-zero common pin 0xC7
        (loader 0x0041FBEC) */
    open_cfw_bl006_u32 cfg_5c; /* 0x2000005C: bank-one pair pin 0x62
        (loader 0x0041FCA2) */
    open_cfw_bl006_u32 cfg_58; /* 0x20000058: bank-one pair pin 0x61
        (loader 0x0041FC96) */
    open_cfw_bl006_u32 cfg_54; /* 0x20000054: bank-one common pin 0x60
        (loader 0x0041FCC6) */
    open_cfw_bl006_u32 cfg_50; /* 0x20000050: bank-one common pin 0x5F
        (loader 0x0041FCBA) */
    open_cfw_bl006_u32 cfg_4c; /* 0x2000004C: bank-one common pin 0x31
        (loader 0x0041FCAE) */
    open_cfw_bl006_u32 cfg_28; /* 0x20000028: bank-zero nine pin 0x25
        (loader 0x0041FB38) */
    open_cfw_bl006_u32 cfg_2c; /* 0x2000002C: bank-zero nine pin 0x26
        (loader 0x0041FB44) */
    open_cfw_bl006_u32 cfg_30; /* 0x20000030: bank-zero nine pin 0x27
        (loader 0x0041FB50) */
    open_cfw_bl006_u32 cfg_34; /* 0x20000034: bank-zero nine pin 0x28
        (loader 0x0041FB5C) */
    open_cfw_bl006_u32 cfg_38; /* 0x20000038: bank-zero nine pin 0x29
        (loader 0x0041FB68) */
    open_cfw_bl006_u32 cfg_3c; /* 0x2000003C: bank-zero nine pin 0x2A
        (loader 0x0041FB74) */
    open_cfw_bl006_u32 cfg_40; /* 0x20000040: bank-zero nine pin 0x2B
        (loader 0x0041FB80) */
    open_cfw_bl006_u32 cfg_44; /* 0x20000044: bank-zero nine pin 0x2C
        (loader 0x0041FB8C) */
    open_cfw_bl006_u32 cfg_48; /* 0x20000048: bank-zero nine pin 0x2D
        (loader 0x0041FB98) */
    open_cfw_bl006_u32 cfg_14; /* 0x20000014: bank-zero quad pin 0x44
        (loader 0x0041FBA4) */
    open_cfw_bl006_u32 cfg_18; /* 0x20000018: bank-zero quad pin 0x45
        (loader 0x0041FBB0) */
    open_cfw_bl006_u32 cfg_1c; /* 0x2000001C: bank-zero quad pin 0x46
        (loader 0x0041FBBC) */
    open_cfw_bl006_u32 cfg_20; /* 0x20000020: bank-zero quad pin 0x47
        (loader 0x0041FBC8) */
    open_cfw_bl006_u32 cfg_24; /* 0x20000024: bank-zero common pin 0x48
        (loader 0x0041FC10) */
    open_cfw_bl006_u32 cfg_60; /* 0x20000060: bank-one quad pin 0x63
        (loader 0x0041FC66) */
    open_cfw_bl006_u32 cfg_64; /* 0x20000064: bank-one quad pin 0x64
        (loader 0x0041FC72) */
    open_cfw_bl006_u32 cfg_68; /* 0x20000068: bank-one quad pin 0x65
        (loader 0x0041FC7E) */
    open_cfw_bl006_u32 cfg_6c; /* 0x2000006C: bank-one quad pin 0x66
        (loader 0x0041FC8A) */
    open_cfw_bl006_u32 cfg_70; /* 0x20000070: bank-one common pin 0x67
        (loader 0x0041FCD2) */
    open_cfw_bl006_u32 cfg_74; /* 0x20000074: bank-one common pin 0x68
        (loader 0x0041FCDE) */
};

__attribute__((used, section(".rodata.bl006_pool_41fcf6")))
const struct open_cfw_bl006_pool_41fcf6 open_cfw_bootloader_bl006_pool_41fcf6 = {
    0x0000u, 0x20000010u, 0x2000000Cu, 0x20000008u, 0x20000004u,
    0x20000000u, 0x2000005Cu, 0x20000058u, 0x20000054u, 0x20000050u,
    0x2000004Cu, 0x20000028u, 0x2000002Cu, 0x20000030u, 0x20000034u,
    0x20000038u, 0x2000003Cu, 0x20000040u, 0x20000044u, 0x20000048u,
    0x20000014u, 0x20000018u, 0x2000001Cu, 0x20000020u, 0x20000024u,
    0x20000060u, 0x20000064u, 0x20000068u, 0x2000006Cu, 0x20000070u,
    0x20000074u
};

/* Pool at 0x0041FDA8: TLSF pool base, handle cell, and diagnostic
 * log arguments consumed by the TLSF pool initializer (stock loaders
 * 0x0041FD78/0x0041FD8C/0x0041FD90/0x0041FD98/0x0041FD9A/0x0041FD9C). */
struct __attribute__((packed)) open_cfw_bl006_pool_41fda8 {
    open_cfw_bl006_u32 alloc_pool; /* 0x20081000: TLSF pool base
        (reviewed allocator host OPEN_CFW_ALLOC_POOL; loader
        0x0041FD78) */
    open_cfw_bl006_u32 alloc_handle; /* 0x2002718C: allocator handle
        cell (reviewed host OPEN_CFW_ALLOC_HANDLE; loader 0x0041FD8C) */
    open_cfw_bl006_u32 log_file; /* 0x00434010: log file path string
        (reviewed host OPEN_CFW_ALLOC_LOG_FILE; loader 0x0041FD90) */
    open_cfw_bl006_u32 log_argument; /* 0x00433CA4: log argument string
        (reviewed host OPEN_CFW_ALLOC_LOG_ARGUMENT; loader 0x0041FD98) */
    open_cfw_bl006_u32 log_format; /* 0x004315C8: log format string
        (reviewed host OPEN_CFW_ALLOC_LOG_FORMAT; loader 0x0041FD9A) */
    open_cfw_bl006_u32 log_tag; /* 0x00434144: log tag string
        (reviewed host OPEN_CFW_ALLOC_LOG_TAG; loader 0x0041FD9C) */
};

__attribute__((used, section(".rodata.bl006_pool_41fda8")))
const struct open_cfw_bl006_pool_41fda8 open_cfw_bootloader_bl006_pool_41fda8 = {
    0x20081000u, 0x2002718Cu, 0x00434010u, 0x00433CA4u, 0x004315C8u,
    0x00434144u
};
