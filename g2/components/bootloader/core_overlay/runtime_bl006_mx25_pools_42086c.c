/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the MX25U25643G shared literal pools at
 * 0x0042086C..0x00420890, 0x00420978..0x00420984,
 * 0x004209BE..0x004209C4, 0x004209FC..0x00420A08,
 * 0x00420ADA..0x00420B0C, 0x00420C18..0x00420C5C,
 * 0x00420DFA..0x00420E08, 0x00420F0C..0x00420F10, and
 * 0x00420F6A..0x00420F70.
 *
 * Every word below names its value, the stock loader PCs that read it
 * (verified by Capstone decode of the authenticated image from each
 * consuming function's exact stock entry, so Thumb decode stays in
 * sync), and its meaning from the already-reviewed consumer sources;
 * see docs/research/g2-bootloader-bl006-cluster-42086c-420f70-source-closure.md
 * for the full loader table. The consumers live in entry-redirect
 * stock spans, so the relocated leaves carry their own copies and
 * these pools are NOT address-live in the final image; they are
 * admitted as authenticated layout reproductions with reviewed
 * meanings, not as live traffic.
 *
 * Two words in this address cluster stay retained for follow-ups:
 * the unidentified literal 0x000081F6 at 0x00420C14 (no loader found
 * in any routed span, named in no reviewed source) and the "set" text
 * tail is ADMITTED here (0x00420F6C, referenced by the reviewed QE
 * service); see the closure doc.
 */

typedef __UINT16_TYPE__ open_cfw_bl006_u16;
typedef __UINT32_TYPE__ open_cfw_bl006_u32;
typedef __UINT8_TYPE__ open_cfw_bl006_u8;

/* Pool at 0x0042086C: zero fill, the NVIC priority-register base,
 * the MSPI state words, and the event-service configuration words,
 * consumed by the IRQ, MSPI control, event-flag, transfer, timing,
 * init, and guard services (stock loaders per slot). */
struct __attribute__((packed)) open_cfw_bl006_pool_42086c {
    open_cfw_bl006_u32 zero_fill; /* 0x00000000: pool alignment; the
        address-mode reader ends at 0x0042086C */
    open_cfw_bl006_u32 nvic_ipr0; /* 0xE000E400: NVIC
        interrupt-priority register 0 (reviewed irq_services host
        OPEN_CFW_NVIC_IPR; loader 0x0041FDE8) */
    open_cfw_bl006_u32 mspi_handle; /* 0x200270DC: MSPI state-handle
        word (reviewed control host OPEN_CFW_MSPI_HANDLE_WORD;
        loaders 0x0041FE38, 0x0041FE4E, 0x0041FF54, 0x00420030,
        0x0042060A, 0x004206AA, 0x00420292) */
    open_cfw_bl006_u32 mspi_active; /* 0x200271C6: MSPI active flag
        (reviewed control host OPEN_CFW_MSPI_ACTIVE; loaders
        0x0041FE2A, 0x0041FE5A) */
    open_cfw_bl006_u32 event_handle; /* 0x200270E0: event-service
        handle cell (reviewed event-flags host
        OPEN_CFW_EVENT_HANDLE_ADDRESS; loaders 0x0041FE64,
        0x0041FE9E, 0x0041FED6) */
    open_cfw_bl006_u32 event_config; /* 0x00433CF8: event-service
        configuration base (reviewed host
        OPEN_CFW_EVENT_CONFIG_ADDRESS; loader 0x0041FE6E) */
    open_cfw_bl006_u32 event_init_format; /* 0x004329FC: event-init
        log format (reviewed host OPEN_CFW_EVENT_INIT_FORMAT;
        loader 0x0041FE7E) */
    open_cfw_bl006_u32 event_init_function; /* 0x0043376C:
        event-init log function (reviewed host
        OPEN_CFW_EVENT_INIT_FUNCTION; loader 0x0041FE88) */
    open_cfw_bl006_u32 event_acquire_format; /* 0x00432CA0:
        event-acquire log format (reviewed host
        OPEN_CFW_EVENT_ACQUIRE_FORMAT; loader 0x0041FEB6) */
};

__attribute__((used, section(".rodata.bl006_pool_42086c")))
const struct open_cfw_bl006_pool_42086c open_cfw_bootloader_bl006_pool_42086c = {
    0x00000000u, 0xE000E400u, 0x200270DCu, 0x200271C6u, 0x200270E0u,
    0x00433CF8u, 0x004329FCu, 0x0043376Cu, 0x00432CA0u
};

/* Pool at 0x00420978: the shared log-file word plus the
 * event-acquire function and event-release format words. */
struct __attribute__((packed)) open_cfw_bl006_pool_420978 {
    open_cfw_bl006_u32 log_file; /* 0x00431540: MX25 log file path
        string (reviewed 4byte-mode host
        OPEN_CFW_4BYTE_MODE_LOG_FILE; loaders 0x0041FE8C,
        0x0041FEC4, 0x0041FEF8, 0x004200D6, 0x00420206, 0x00420242,
        the six low-init sites, the three driver-init sites, the
        two soft-reset sites, 0x004205C8, 0x00420780, 0x00420832,
        0x0042085C, 0x004208B8, 0x004208E0, 0x00420914, 0x0042093E,
        0x00420966; later MX25 functions load the duplicate word
        at 0x00421030 instead) */
    open_cfw_bl006_u32 event_acquire_function; /* 0x00433784:
        event-acquire log function (reviewed event-flags host
        OPEN_CFW_EVENT_ACQUIRE_FUNCTION; loader 0x0041FEC0) */
    open_cfw_bl006_u32 event_release_format; /* 0x00432A24:
        event-release log format (reviewed host
        OPEN_CFW_EVENT_RELEASE_FORMAT; loader 0x0041FEEA) */
};

__attribute__((used, section(".rodata.bl006_pool_420978")))
const struct open_cfw_bl006_pool_420978 open_cfw_bootloader_bl006_pool_420978 = {
    0x00431540u, 0x00433784u, 0x00432A24u
};

/* Island at 0x004209BE: two-byte fill plus the event-release log
 * function word (the write-enable wrapper ends at 0x004209BE). */
struct __attribute__((packed)) open_cfw_bl006_island_4209be {
    open_cfw_bl006_u16 align_fill; /* 0x0000: pool alignment */
    open_cfw_bl006_u32 event_release_function; /* 0x0043379C:
        event-release log function (reviewed event-flags host
        OPEN_CFW_EVENT_RELEASE_FUNCTION; loader 0x0041FEF4) */
};

__attribute__((used, section(".rodata.bl006_island_4209be")))
const struct open_cfw_bl006_island_4209be open_cfw_bootloader_bl006_island_4209be = {
    0x0000u, 0x0043379Cu
};

/* Pool at 0x004209FC: NVIC/system-handler bases plus the shared
 * timing-active address (the write-disable wrapper ends at
 * 0x004209FC). */
struct __attribute__((packed)) open_cfw_bl006_pool_4209fc {
    open_cfw_bl006_u32 nvic_iser0; /* 0xE000E100: NVIC
        interrupt-set-enable register 0 (reviewed irq_services
        host OPEN_CFW_NVIC_ISER; loader 0x0041FDD0) */
    open_cfw_bl006_u32 scb_shpr2; /* 0xE000ED18: System Control
        Block system-handler-priority register 2 (reviewed host
        OPEN_CFW_SCB_SHP; loader 0x0041FDF4) */
    open_cfw_bl006_u32 timing_active; /* 0x2000023C: timing/XIP
        active address (reviewed timing-auto host
        OPEN_CFW_TIMING_AUTO_ACTIVE_ADDRESS and XIP host
        OPEN_CFW_MSPI_XIP_CONFIG_ADDRESS; loaders 0x0041FF3E,
        0x0041FF48, 0x0041FF4E, 0x004201D2, 0x00420216) */
};

__attribute__((used, section(".rodata.bl006_pool_4209fc")))
const struct open_cfw_bl006_pool_4209fc open_cfw_bootloader_bl006_pool_4209fc = {
    0xE000E100u, 0xE000ED18u, 0x2000023Cu
};

/* Pool at 0x00420ADA: two-byte fill plus the shared MX25 log tag
 * and the timing-scan, timing-auto, guard, and low-init words
 * (the sector-erase service ends at 0x00420ADA). */
struct __attribute__((packed)) open_cfw_bl006_pool_420ada {
    open_cfw_bl006_u16 align_fill; /* 0x0000: pool alignment */
    open_cfw_bl006_u32 log_tag; /* 0x00433CD8: "drv.norflash" log
        tag (reviewed write-latch host
        OPEN_CFW_WRITE_LATCH_LOG_TAG; loaders 0x0041FE90,
        0x0041FEC8, 0x0041FEFC, 0x004200D2, 0x0042020A, 0x00420246,
        the six low-init sites, the three driver-init sites, the
        two soft-reset sites, 0x004205CC, 0x00420782, 0x00420834,
        0x0042085E, 0x004208BA, 0x004208E2, 0x00420916, 0x00420940,
        0x00420968, 0x004209F0, 0x00420A32; later MX25 functions
        load the duplicate word at 0x00421034 instead) */
    open_cfw_bl006_u32 guard_bypass; /* 0x200271C5: MSPI guard
        bypass address (reviewed guard host
        OPEN_CFW_MSPI_GUARD_BYPASS_ADDRESS; loaders 0x0041FF0E,
        0x0041FF20) */
    open_cfw_bl006_u32 timing_expected_id; /* 0x002539C2:
        timing-scan expected device ID (reviewed timing-scan
        host OPEN_CFW_TIMING_EXPECTED_ID; loader 0x00420046) */
    open_cfw_bl006_u32 timing_table; /* 0x20000244: timing table
        address (reviewed host OPEN_CFW_TIMING_TABLE_ADDRESS;
        loaders 0x00420070, 0x004200FC) */
    open_cfw_bl006_u32 timing_log_function; /* 0x00433AB0:
        timing-scan log function (reviewed host
        OPEN_CFW_TIMING_LOG_FUNCTION; loader 0x004200DA) */
    open_cfw_bl006_u32 timing_summary_format; /* 0x0043160C:
        timing summary format (reviewed host
        OPEN_CFW_TIMING_LOG_SUMMARY_FORMAT; loader 0x004200E2) */
    open_cfw_bl006_u32 timing_row_format; /* 0x004313D8:
        timing row format (reviewed host
        OPEN_CFW_TIMING_LOG_ROW_FORMAT; loader 0x0042013A) */
    open_cfw_bl006_u32 timing_auto_success_format; /* 0x00430BD0:
        timing-auto success format (reviewed timing-auto host
        OPEN_CFW_TIMING_AUTO_SUCCESS_FORMAT; loader 0x004201F6) */
    open_cfw_bl006_u32 timing_auto_function; /* 0x004337B4:
        timing-auto log function (reviewed host
        OPEN_CFW_TIMING_AUTO_LOG_FUNCTION; loaders 0x00420202,
        0x0042023E) */
    open_cfw_bl006_u32 timing_auto_failure_format; /* 0x00430C4C:
        timing-auto failure format (reviewed host
        OPEN_CFW_TIMING_AUTO_FAILURE_FORMAT; loader 0x00420232) */
    open_cfw_bl006_u32 low_init_state; /* 0x20026FD0: low-level
        init state address (reviewed low-init host
        OPEN_CFW_LOW_INIT_STATE_ADDRESS; loaders 0x00420278,
        0x0042041C) */
    open_cfw_bl006_u32 low_init_power_format; /* 0x00432CC4:
        low-init power format (reviewed host
        OPEN_CFW_LOW_INIT_POWER_FORMAT; loader 0x004202B4) */
};

__attribute__((used, section(".rodata.bl006_pool_420ada")))
const struct open_cfw_bl006_pool_420ada open_cfw_bootloader_bl006_pool_420ada = {
    0x0000u, 0x00433CD8u, 0x200271C5u, 0x002539C2u, 0x20000244u,
    0x00433AB0u, 0x0043160Cu, 0x004313D8u, 0x00430BD0u, 0x004337B4u,
    0x00430C4Cu, 0x20026FD0u, 0x00432CC4u
};

/* Pool at 0x00420C18 (suffix of the 0x00420C14 region): the
 * timing-center format plus the low-init, serial-template,
 * driver-init, and soft-reset words. The leading word at
 * 0x00420C14 (0x000081F6) has no loader in any routed span and is
 * named in no reviewed source, so it stays retained; see the
 * closure doc. */
struct __attribute__((packed)) open_cfw_bl006_pool_420c18 {
    open_cfw_bl006_u32 timing_center_format; /* 0x004334B4:
        timing-scan center format (reviewed timing-scan host
        OPEN_CFW_TIMING_LOG_CENTER_FORMAT; loader 0x00420162) */
    open_cfw_bl006_u32 low_init_log_function; /* 0x00433180:
        low-init log function (reviewed low-init host
        OPEN_CFW_LOW_INIT_LOG_FUNCTION; loaders 0x004202C0,
        0x00420306, 0x00420356, 0x00420390, 0x004203F4, 0x0042045C) */
    open_cfw_bl006_u32 low_init_tcb; /* 0x200F4C00: low-init TCB
        address (reviewed host OPEN_CFW_LOW_INIT_TCB_ADDRESS;
        loader 0x004202DC) */
    open_cfw_bl006_u32 low_init_configure_format; /* 0x00432CE8:
        low-init configure format (reviewed host
        OPEN_CFW_LOW_INIT_CONFIGURE_FORMAT; loader 0x004202FA) */
    open_cfw_bl006_u32 low_init_default_config; /* 0x20000224:
        low-init default-config address (reviewed host
        OPEN_CFW_LOW_INIT_DEFAULT_CONFIG_ADDRESS; loader
        0x00420336) */
    open_cfw_bl006_u32 low_init_device_format; /* 0x00432624:
        low-init device format (reviewed host
        OPEN_CFW_LOW_INIT_DEVICE_FORMAT; loader 0x0042034A) */
    open_cfw_bl006_u32 low_init_enable_format; /* 0x004331A0:
        low-init enable format (reviewed host
        OPEN_CFW_LOW_INIT_ENABLE_FORMAT; loader 0x00420384) */
    open_cfw_bl006_u32 low_init_interrupt_format; /* 0x00432A4C:
        low-init interrupt format (reviewed host
        OPEN_CFW_LOW_INIT_INTERRUPT_FORMAT; loader 0x004203E8) */
    open_cfw_bl006_u32 serial_template; /* 0x2000020C:
        serial-mode template address (reviewed serial-mode
        host OPEN_CFW_SERIAL_TEMPLATE_ADDRESS; loader 0x0042042C) */
    open_cfw_bl006_u32 low_init_success_format; /* 0x00432A74:
        low-init success format (reviewed host
        OPEN_CFW_LOW_INIT_SUCCESS_FORMAT; loader 0x00420450) */
    open_cfw_bl006_u32 driver_state; /* 0x200270D8: driver-init
        state slot (reviewed driver-init host
        OPEN_CFW_DRIVER_INIT_STATE_SLOT; loader 0x00420478) */
    open_cfw_bl006_u32 driver_fail_format; /* 0x004337E4:
        driver-init fail format (reviewed host
        OPEN_CFW_DRIVER_INIT_FAIL_FORMAT; loader 0x0042048C) */
    open_cfw_bl006_u32 driver_log_function; /* 0x004337CC:
        driver-init log function (reviewed host
        OPEN_CFW_DRIVER_INIT_LOG_FUNCTION; loaders 0x00420498,
        0x004204DC, 0x00420500) */
    open_cfw_bl006_u32 driver_id_fail_format; /* 0x00433AC4:
        driver ID-fail format (reviewed host
        OPEN_CFW_DRIVER_ID_FAIL_FORMAT; loader 0x004204D0) */
    open_cfw_bl006_u32 driver_id_format; /* 0x00433AD8:
        driver ID format (reviewed host
        OPEN_CFW_DRIVER_ID_FORMAT; loader 0x004204F4) */
    open_cfw_bl006_u32 soft_reset_enable_format; /* 0x004334EC:
        soft-reset enable format (reviewed soft-reset host
        OPEN_CFW_SOFT_RESET_ENABLE_FORMAT; loader 0x00420540) */
    open_cfw_bl006_u32 soft_reset_log_function; /* 0x004334D0:
        soft-reset log function (reviewed host
        OPEN_CFW_SOFT_RESET_LOG_FUNCTION; loaders 0x0042054C,
        0x00420584) */
};

__attribute__((used, section(".rodata.bl006_pool_420c18")))
const struct open_cfw_bl006_pool_420c18 open_cfw_bootloader_bl006_pool_420c18 = {
    0x004334B4u, 0x00433180u, 0x200F4C00u, 0x00432CE8u, 0x20000224u,
    0x00432624u, 0x004331A0u, 0x00432A4Cu, 0x2000020Cu, 0x00432A74u,
    0x200270D8u, 0x004337E4u, 0x004337CCu, 0x00433AC4u, 0x00433AD8u,
    0x004334ECu, 0x004334D0u
};

/* Pool at 0x00420DFA: two-byte fill plus the shared log format
 * and the read-ID function/format words (the QE service ends at
 * 0x00420DFA). */
struct __attribute__((packed)) open_cfw_bl006_pool_420dfa {
    open_cfw_bl006_u16 align_fill; /* 0x0000: pool alignment */
    open_cfw_bl006_u32 log_format; /* 0x00432650: shared log
        format (reviewed write-latch host
        OPEN_CFW_WRITE_LATCH_LOG_FORMAT and soft-reset host
        OPEN_CFW_SOFT_RESET_FORMAT; loaders 0x0042099C,
        0x004209DC, 0x00420578) */
    open_cfw_bl006_u32 read_id_fail_format; /* 0x00433AEC:
        read-ID fail format (reviewed read-ID host
        OPEN_CFW_READ_ID_FAIL_FORMAT; loader 0x004205B8) */
    open_cfw_bl006_u32 read_id_log_function; /* 0x004337FC:
        read-ID log function (reviewed host
        OPEN_CFW_READ_ID_LOG_FUNCTION; loader 0x004205C4) */
};

__attribute__((used, section(".rodata.bl006_pool_420dfa")))
const struct open_cfw_bl006_pool_420dfa open_cfw_bootloader_bl006_pool_420dfa = {
    0x0000u, 0x00432650u, 0x00433AECu, 0x004337FCu
};

/* Word at 0x00420F0C: the one-microsecond transfer timeout shared
 * by the read/write transfer services and the read service. */
__attribute__((used, section(".rodata.bl006_word_420f0c")))
const open_cfw_bl006_u32 open_cfw_bootloader_bl006_word_420f0c = 1000000u;

/* Text at 0x00420F6A: two-byte fill plus the NUL-terminated "set"
 * text selected by the QE service (the serial-mode service ends at
 * 0x00420F6A). */
struct __attribute__((packed)) open_cfw_bl006_text_420f6a {
    open_cfw_bl006_u16 align_fill; /* 0x0000: pool alignment */
    open_cfw_bl006_u8 text[4]; /* "set\0": QE set text (reviewed
        QE host OPEN_CFW_QUAD_SET_TEXT = 0x00420F6C; selected by
        adr at stock loader 0x00420DD2, falling through to the
        clear text otherwise) */
};

__attribute__((used, section(".rodata.bl006_text_420f6a")))
const struct open_cfw_bl006_text_420f6a open_cfw_bootloader_bl006_text_420f6a = {
    0x0000u, {0x73u, 0x65u, 0x74u, 0x00u}
};
