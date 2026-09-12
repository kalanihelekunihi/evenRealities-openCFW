/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the LittleFS-adjacent shared literal pools at
 * 0x00420FF2..0x004210C8, 0x00421372..0x004213D4, and
 * 0x0042156E..0x00421584.
 *
 * Every word below names its value, the stock loader PCs that read it
 * (verified by Capstone decode of the authenticated image from each
 * consuming function's exact stock entry, so Thumb decode stays in
 * sync), and its meaning from the already-reviewed consumer sources;
 * see docs/research/g2-bootloader-bl006-cluster-420ff2-421584-source-closure.md
 * for the full loader tables. The MX25/LittleFS consumers live in
 * entry-redirect stock spans, so the relocated leaves carry their own
 * copies; the mapped-memory selector consumers at 0x004213EC..0x00421548
 * are compiled in place and read the 0x0042156E pool live. All three
 * pools are admitted as authenticated layout reproductions with reviewed
 * meanings.
 */

typedef __UINT16_TYPE__ open_cfw_bl006_u16;
typedef __UINT32_TYPE__ open_cfw_bl006_u32;

/* Pool at 0x00420FF2: two-byte fill plus the MX25 transfer, status,
 * address-mode, 4byte-mode, latch, erase, program, QE, reconfigure,
 * quad-mode, serial-mode, and read-service literal words. */
struct __attribute__((packed)) open_cfw_bl006_pool_420ff2 {
    open_cfw_bl006_u16 align_fill; /* 0x0000: pool alignment */
    open_cfw_bl006_u32 read_transfer_log_format; /* 0x00431420:
        read-transfer log format (reviewed read-transfer host
        OPEN_CFW_READ_TRANSFER_LOG_FORMAT; loader 0x0042068E) */
    open_cfw_bl006_u32 write_transfer_log_format; /* 0x00431468:
        write-transfer log format (reviewed write-transfer host
        OPEN_CFW_WRITE_TRANSFER_LOG_FORMAT; loader 0x0042073E) */
    open_cfw_bl006_u32 busy_fail_format; /* 0x00433508: busy-status
        fail format (reviewed busy-status host
        OPEN_CFW_BUSY_STATUS_FAIL_FORMAT; loader 0x00420770) */
    open_cfw_bl006_u32 busy_log_function; /* 0x00433B00: busy-status
        log function (reviewed host
        OPEN_CFW_BUSY_STATUS_LOG_FUNCTION; loader 0x0042077C) */
    open_cfw_bl006_u32 addr_mode_read_fail_format; /* 0x00433814:
        address-mode read-fail format (reviewed 4byte-mode host
        OPEN_CFW_4BYTE_MODE_READ_FAIL_FORMAT; loader 0x00420822) */
    open_cfw_bl006_u32 addr_mode_log_function; /* 0x00433524:
        address-mode log function (reviewed host
        OPEN_CFW_4BYTE_MODE_LOG_FUNCTION; loaders 0x0042082E,
        0x00420858) */
    open_cfw_bl006_u32 addr_mode_three_byte_format; /* 0x00432D0C:
        address-mode three-byte format (reviewed host
        OPEN_CFW_4BYTE_MODE_THREE_BYTE_FORMAT; loader 0x0042084C) */
    open_cfw_bl006_u32 mspi_state_handle; /* 0x200270DC: MSPI
        state-handle word (enter-4byte availability check on the
        bare literal, plus erase, program, QE, reconfigure,
        quad-mode, serial-mode, and read-service hosts; loaders
        0x00420892, 0x00420A0C, 0x00420B18, 0x00420C62,
        0x00420E0C, 0x00420EE4, 0x00420F44, 0x00420F7A) */
    open_cfw_bl006_u32 enter_4byte_busy_format; /* 0x00433CE8:
        enter-4byte busy format (reviewed host
        OPEN_CFW_ENTER_4BYTE_BUSY_FORMAT; loader 0x004208A8) */
    open_cfw_bl006_u32 enter_4byte_log_function; /* 0x004331C0:
        enter-4byte log function (reviewed host
        OPEN_CFW_ENTER_4BYTE_LOG_FUNCTION; loaders 0x004208B4,
        0x004208DC, 0x00420910, 0x0042093A, 0x00420962) */
    open_cfw_bl006_u32 enter_4byte_enable_format; /* 0x00431ED8:
        enter-4byte enable format (reviewed host
        OPEN_CFW_ENTER_4BYTE_ENABLE_FORMAT; loader 0x004208D0) */
    open_cfw_bl006_u32 enter_4byte_command_format; /* 0x004331E0:
        enter-4byte command format (reviewed host
        OPEN_CFW_ENTER_4BYTE_COMMAND_FORMAT; loader 0x00420904) */
    open_cfw_bl006_u32 enter_4byte_verify_format; /* 0x00433200:
        enter-4byte verify format (reviewed host
        OPEN_CFW_ENTER_4BYTE_VERIFY_FORMAT; loader 0x0042092E) */
    open_cfw_bl006_u32 enter_4byte_disable_format; /* 0x0043382C:
        enter-4byte disable format (reviewed host
        OPEN_CFW_ENTER_4BYTE_DISABLE_FORMAT; loader 0x00420956) */
    open_cfw_bl006_u32 write_enable_log_function; /* 0x00433220:
        write-enable log function (reviewed latch host
        OPEN_CFW_WRITE_ENABLE_LOG_FUNCTION; loader 0x004209A8) */
    open_cfw_bl006_u32 shared_log_file; /* 0x00431540: shared log
        file path (reviewed latch host
        OPEN_CFW_WRITE_LATCH_LOG_FILE and QE host
        OPEN_CFW_QUAD_LOG_FILE; loaders 0x004209AC, 0x004209EC,
        0x00420A2E, 0x00420C9A, 0x00420CE8, 0x00420D14,
        0x00420D74, 0x00420DA8, 0x00420DE6, 0x00420E24,
        0x00420E4A, 0x00420E6E, 0x00420EC8, 0x00420EFC,
        0x00420F28, 0x00420F5C) */
    open_cfw_bl006_u32 shared_log_tag; /* 0x00433CD8: shared
        "drv.norflash" log tag (reviewed latch host
        OPEN_CFW_WRITE_LATCH_LOG_TAG and QE host
        OPEN_CFW_QUAD_LOG_TAG; loaders 0x004209B0, 0x00420C9E,
        0x00420CEC, 0x00420D16, 0x00420D76, 0x00420DAA,
        0x00420DE8, 0x00420E26, 0x00420E4C, 0x00420E70,
        0x00420ECA, 0x00420EFE, 0x00420F2A, 0x00420F5E) */
    open_cfw_bl006_u32 write_disable_log_function; /* 0x00432D30:
        write-disable log function (reviewed latch host
        OPEN_CFW_WRITE_DISABLE_LOG_FUNCTION; loader 0x004209E8) */
    open_cfw_bl006_u32 sector_erase_align_format; /* 0x00432D54:
        sector-erase align format (reviewed erase host
        OPEN_CFW_SECTOR_ERASE_ALIGN_FORMAT; loader 0x00420A1E) */
    open_cfw_bl006_u32 sector_erase_log_function; /* 0x00433540:
        sector-erase log function (reviewed host
        OPEN_CFW_SECTOR_ERASE_LOG_FUNCTION; loader 0x00420A2A) */
    open_cfw_bl006_u32 sector_erase_prewait_format; /* 0x00432148:
        sector-erase prewait format (reviewed host
        OPEN_CFW_SECTOR_ERASE_PREWAIT_FORMAT; loader 0x00420A5A) */
    open_cfw_bl006_u32 sector_erase_enable_format; /* 0x0043267C:
        sector-erase enable format (reviewed host
        OPEN_CFW_SECTOR_ERASE_ENABLE_FORMAT; loader 0x00420A74) */
    open_cfw_bl006_u32 sector_erase_command_format; /* 0x00432178:
        sector-erase command format (reviewed host
        OPEN_CFW_SECTOR_ERASE_COMMAND_FORMAT; loader 0x00420A98) */
    open_cfw_bl006_u32 sector_erase_postwait_format; /* 0x004321A8:
        sector-erase postwait format (reviewed host
        OPEN_CFW_SECTOR_ERASE_POSTWAIT_FORMAT; loader 0x00420AAC) */
    open_cfw_bl006_u32 sector_erase_disable_format; /* 0x004321D8:
        sector-erase disable format (reviewed host
        OPEN_CFW_SECTOR_ERASE_DISABLE_FORMAT; loader 0x00420AC6) */
    open_cfw_bl006_u32 program_invalid_format; /* 0x004326A8:
        page-program invalid format (reviewed program host
        OPEN_CFW_PROGRAM_INVALID_FORMAT; loader 0x00420B30) */
    open_cfw_bl006_u32 program_range_format; /* 0x004326D4:
        page-program range format (reviewed host
        OPEN_CFW_PROGRAM_RANGE_FORMAT; loader 0x00420B48) */
    open_cfw_bl006_u32 program_prewait_format; /* 0x00431AF0:
        page-program prewait format (reviewed host
        OPEN_CFW_PROGRAM_PREWAIT_FORMAT; loader 0x00420BBE) */
    open_cfw_bl006_u32 program_enable_format; /* 0x00431F0C:
        page-program enable format (reviewed host
        OPEN_CFW_PROGRAM_ENABLE_FORMAT; loader 0x00420BD0) */
    open_cfw_bl006_u32 program_transfer_format; /* 0x00432208:
        page-program transfer format (reviewed host
        OPEN_CFW_PROGRAM_TRANSFER_FORMAT; loader 0x00420BE0) */
    open_cfw_bl006_u32 program_postwait_format; /* 0x00431B28:
        page-program postwait format (reviewed host
        OPEN_CFW_PROGRAM_POSTWAIT_FORMAT; loader 0x00420BEE) */
    open_cfw_bl006_u32 program_disable_format; /* 0x00431B60:
        page-program disable format (reviewed host
        OPEN_CFW_PROGRAM_DISABLE_FORMAT; loader 0x00420C00) */
    open_cfw_bl006_u32 quad_read_fail_format; /* 0x00432D78: QE
        read-fail format (reviewed QE host
        OPEN_CFW_QUAD_READ_FAIL_FORMAT; loader 0x00420C8A) */
    open_cfw_bl006_u32 quad_enable_log_function; /* 0x00433844: QE
        log function (reviewed host OPEN_CFW_QUAD_LOG_FUNCTION;
        loaders 0x00420C96, 0x00420CE4, 0x00420D10, 0x00420D72,
        0x00420DA6, 0x00420DE4) */
    open_cfw_bl006_u32 quad_unchanged_format; /* 0x00432D9C: QE
        unchanged format (reviewed host
        OPEN_CFW_QUAD_UNCHANGED_FORMAT; loader 0x00420CD8) */
    open_cfw_bl006_u32 quad_enable_fail_format; /* 0x00432A9C: QE
        enable-fail format (reviewed host
        OPEN_CFW_QUAD_ENABLE_FAIL_FORMAT; loader 0x00420D04) */
    open_cfw_bl006_u32 quad_write_fail_format; /* 0x00432DC0: QE
        write-fail format (reviewed host
        OPEN_CFW_QUAD_WRITE_FAIL_FORMAT; loader 0x00420D66) */
    open_cfw_bl006_u32 quad_verify_read_fail_format; /* 0x0043355C:
        QE verify-read-fail format (reviewed host
        OPEN_CFW_QUAD_VERIFY_READ_FAIL_FORMAT; loader 0x00420D9C) */
    open_cfw_bl006_u32 quad_clear_text; /* 0x00434034: QE "clear"
        text (reviewed QE host OPEN_CFW_QUAD_CLEAR_TEXT; loader
        0x00420DD6) */
    open_cfw_bl006_u32 quad_verify_fail_format; /* 0x0043385C: QE
        verify-fail format (reviewed host
        OPEN_CFW_QUAD_VERIFY_FAIL_FORMAT; loader 0x00420DDA) */
    open_cfw_bl006_u32 reconfig_disable_format; /* 0x00432E08:
        reconfigure disable format (reviewed reconfigure host
        OPEN_CFW_RECONFIGURE_DISABLE_FORMAT; loader 0x00420E18) */
    open_cfw_bl006_u32 reconfig_log_function; /* 0x00432DE4:
        reconfigure log function (reviewed host
        OPEN_CFW_RECONFIGURE_LOG_FUNCTION; loaders 0x00420E22,
        0x00420E48, 0x00420E6C) */
    open_cfw_bl006_u32 reconfig_configure_format; /* 0x00432E2C:
        reconfigure configure format (reviewed host
        OPEN_CFW_RECONFIGURE_CONFIGURE_FORMAT; loaders 0x00420E3E,
        0x00420E62) */
    open_cfw_bl006_u32 reconfig_state_address; /* 0x200270D8:
        reconfigure state slot (reviewed host
        OPEN_CFW_RECONFIGURE_STATE_ADDRESS; loader 0x00420E7E) */
    open_cfw_bl006_u32 quad_template_address; /* 0x20000224:
        quad-mode template address (reviewed quad-mode host
        OPEN_CFW_QUAD_TEMPLATE_ADDRESS; loader 0x00420E92) */
    open_cfw_bl006_u32 quad_reconfig_format; /* 0x00432E50:
        quad-mode reconfigure format (reviewed host
        OPEN_CFW_QUAD_RECONFIGURE_FORMAT; loader 0x00420EBC) */
    open_cfw_bl006_u32 quad_mode_log_function; /* 0x00433578:
        quad-mode log function (reviewed host
        OPEN_CFW_QUAD_LOG_FUNCTION; loaders 0x00420EC6,
        0x00420EFA) */
    open_cfw_bl006_u32 quad_control_format; /* 0x00433240:
        quad-mode control format (reviewed host
        OPEN_CFW_QUAD_CONTROL_FORMAT; loader 0x00420EF0) */
    open_cfw_bl006_u32 serial_template_address; /* 0x2000020C:
        serial-mode template address (reviewed serial-mode host
        OPEN_CFW_SERIAL_TEMPLATE_ADDRESS; loader 0x00420F12) */
    open_cfw_bl006_u32 serial_reconfig_format; /* 0x00432E74:
        serial-mode reconfigure format (reviewed host
        OPEN_CFW_SERIAL_RECONFIGURE_FORMAT; loader 0x00420F1C) */
    open_cfw_bl006_u32 serial_log_function; /* 0x00433594:
        serial-mode log function (reviewed host
        OPEN_CFW_SERIAL_LOG_FUNCTION; loaders 0x00420F26,
        0x00420F5A) */
    open_cfw_bl006_u32 serial_control_format; /* 0x00433260:
        serial-mode control format (reviewed host
        OPEN_CFW_SERIAL_CONTROL_FORMAT; loader 0x00420F50) */
    open_cfw_bl006_u32 read_timeout; /* 0x000F4240: one-microsecond
        read timeout (reviewed read host
        OPEN_CFW_MSPI_READ_TIMEOUT = 1000000; loader 0x00420FDC) */
};

__attribute__((used, section(".rodata.bl006_pool_420ff2")))
const struct open_cfw_bl006_pool_420ff2 open_cfw_bootloader_bl006_pool_420ff2 = {
    0x0000u, 0x00431420u, 0x00431468u, 0x00433508u, 0x00433B00u,
    0x00433814u, 0x00433524u, 0x00432D0Cu, 0x200270DCu, 0x00433CE8u,
    0x004331C0u, 0x00431ED8u, 0x004331E0u, 0x00433200u, 0x0043382Cu,
    0x00433220u, 0x00431540u, 0x00433CD8u, 0x00432D30u, 0x00432D54u,
    0x00433540u, 0x00432148u, 0x0043267Cu, 0x00432178u, 0x004321A8u,
    0x004321D8u, 0x004326A8u, 0x004326D4u, 0x00431AF0u, 0x00431F0Cu,
    0x00432208u, 0x00431B28u, 0x00431B60u, 0x00432D78u, 0x00433844u,
    0x00432D9Cu, 0x00432A9Cu, 0x00432DC0u, 0x0043355Cu, 0x00434034u,
    0x0043385Cu, 0x00432E08u, 0x00432DE4u, 0x00432E2Cu, 0x200270D8u,
    0x20000224u, 0x00432E50u, 0x00433578u, 0x00433240u, 0x2000020Cu,
    0x00432E74u, 0x00433594u, 0x00433260u, 1000000u
};

/* Pool at 0x00421372: two-byte fill plus the directory-bootstrap,
 * format, init, and block-callback literal words. The stock init body
 * at 0x00421210..0x004212D8 reads the 0x004213AC..0x004213C4 slots;
 * the relocated init leaf carries its own copies. */
struct __attribute__((packed)) open_cfw_bl006_pool_421372 {
    open_cfw_bl006_u16 align_fill; /* 0x0000: pool alignment */
    open_cfw_bl006_u32 dir_paths_address; /* 0x00433E58: directory
        paths table (reviewed dir-bootstrap host
        OPEN_CFW_FS_DIRECTORIES_PATHS_ADDRESS; loader 0x004210CE) */
    open_cfw_bl006_u32 dir_created_format; /* 0x00433934:
        directory-created format (reviewed host, created log call;
        loader 0x004210E2) */
    open_cfw_bl006_u32 dir_log_function; /* 0x00433300: shared
        directory log function (reviewed host, log helper;
        loaders 0x004210EA, 0x0042110E, 0x00421158, 0x00421176,
        0x00421198) */
    open_cfw_bl006_u32 shared_log_file; /* 0x00430E60: shared log
        file path (reviewed dir-bootstrap, format, and init
        hosts; loaders 0x004210EC, 0x00421110, 0x0042115A,
        0x00421178, 0x0042119A, 0x004211DE, 0x004211FE,
        0x00421244, 0x00421264, 0x004212C8) */
    open_cfw_bl006_u32 shared_log_tag; /* 0x00433FBC: shared log
        tag (reviewed dir-bootstrap, format, and init hosts;
        loaders 0x004210EE, 0x00421112, 0x0042115C, 0x0042117A,
        0x0042119C, 0x004211E0, 0x00421200, 0x00421246,
        0x00421266, 0x004212CA) */
    open_cfw_bl006_u32 dir_present_format; /* 0x0043394C:
        directory-present format (reviewed host, present log
        call; loader 0x00421106) */
    open_cfw_bl006_u32 dir_lfs_address; /* 0x20026878: LittleFS
        object address (reviewed dir-bootstrap host
        OPEN_CFW_FS_DIRECTORIES_LFS_ADDRESS; loaders 0x00421120,
        0x004211B4, 0x00421214) */
    open_cfw_bl006_u32 dir_exists_format; /* 0x00433320:
        already-exists format (reviewed host, exists log call;
        loader 0x00421150) */
    open_cfw_bl006_u32 dir_create_failed_format; /* 0x00432FDC:
        create-failed format (reviewed host, failed log call;
        loader 0x0042116E) */
    open_cfw_bl006_u32 dir_check_failed_format; /* 0x00433340:
        check-failed format (reviewed host, default log call;
        loader 0x00421190) */
    open_cfw_bl006_u32 format_config_address; /* 0x00431070:
        format config address (reviewed format host
        OPEN_CFW_LITTLEFS_FORMAT_CONFIG_ADDRESS; loaders
        0x004211BC, 0x00421216) */
    open_cfw_bl006_u32 format_mount_failed_format; /* 0x00433964:
        format mount-failed format (reviewed host, mount-failed
        log call; loader 0x004211D4) */
    open_cfw_bl006_u32 format_log_function; /* 0x00433E28: format
        log function (reviewed host, log helper; loaders
        0x004211DC, 0x004211FC) */
    open_cfw_bl006_u32 format_failed_format; /* 0x00433000:
        format-failed format (reviewed host, failed log call;
        loader 0x004211F4) */
    open_cfw_bl006_u32 init_mount_failed_format; /* 0x0043397C:
        init mount-failed format (reviewed init host,
        mount-failed log call; loader 0x0042123A) */
    open_cfw_bl006_u32 init_log_function; /* 0x00433E38: init log
        function (reviewed host, log helper; loaders 0x00421242,
        0x00421262, 0x004212C6) */
    open_cfw_bl006_u32 init_directories_failed_format; /* 0x0043178C:
        init directories-failed format (reviewed host,
        directories-failed log call; loader 0x0042125A) */
    open_cfw_bl006_u32 init_ready_address; /* 0x2002711C: init
        ready flag (reviewed host
        OPEN_CFW_LITTLEFS_INIT_READY_ADDRESS; loader 0x00421274) */
    open_cfw_bl006_u32 init_file_address; /* 0x20026C0C: init file
        object (reviewed host OPEN_CFW_LITTLEFS_INIT_FILE_ADDRESS;
        loader 0x0042127C) */
    open_cfw_bl006_u32 init_file_path; /* 0x00433FC8: init file
        path (reviewed host, file-open call; loader 0x00421282) */
    open_cfw_bl006_u32 init_mounted_format; /* 0x00433E48: init
        mounted format (reviewed host, mounted log call; loader
        0x004212BE) */
    open_cfw_bl006_u32 block_read_log_format; /* 0x004317CC:
        block-read log format (reviewed read-callback host,
        log call; loader 0x00421300) */
    open_cfw_bl006_u32 block_prog_log_format; /* 0x0043180C:
        block-program log format (reviewed program-callback
        host, log call; loader 0x00421338) */
    open_cfw_bl006_u32 block_erase_log_format; /* 0x00432568:
        block-erase log format (reviewed erase-callback host,
        log call; loader 0x00421362) */
};

__attribute__((used, section(".rodata.bl006_pool_421372")))
const struct open_cfw_bl006_pool_421372 open_cfw_bootloader_bl006_pool_421372 = {
    0x0000u, 0x00433E58u, 0x00433934u, 0x00433300u, 0x00430E60u,
    0x00433FBCu, 0x0043394Cu, 0x20026878u, 0x00433320u, 0x00432FDCu,
    0x00433340u, 0x00431070u, 0x00433964u, 0x00433E28u, 0x00433000u,
    0x0043397Cu, 0x00433E38u, 0x0043178Cu, 0x2002711Cu, 0x20026C0Cu,
    0x00433FC8u, 0x00433E48u, 0x004317CCu, 0x0043180Cu, 0x00432568u
};

/* Pool at 0x0042156E: two-byte fill plus the mapped-memory control,
 * security, and window-base words, read live by the in-place
 * selector and odd-selector wrapper. */
struct __attribute__((packed)) open_cfw_bl006_pool_42156e {
    open_cfw_bl006_u16 align_fill; /* 0x0000: pool alignment */
    open_cfw_bl006_u32 memory_control; /* 0x400201BC: memory
        control register (reviewed selector host
        OPEN_CFW_MEMORY_SELECT_CONTROL; loader 0x004213F2) */
    open_cfw_bl006_u32 memory_security; /* 0x40021008: memory
        security register (reviewed host
        OPEN_CFW_MEMORY_SELECT_SECURITY; loader 0x00421408) */
    open_cfw_bl006_u32 window_base_two; /* 0x42004000: window-two
        base (reviewed host OPEN_CFW_MEMORY_SELECT_BASE_TWO;
        loaders 0x004214B6, 0x00421502) */
    open_cfw_bl006_u32 window_base_three; /* 0x42006000:
        window-three base (reviewed host
        OPEN_CFW_MEMORY_SELECT_BASE_THREE; loaders 0x004214E0,
        0x00421518) */
    open_cfw_bl006_u32 window_base_one; /* 0x42002000: window-one
        base (reviewed host OPEN_CFW_MEMORY_SELECT_BASE_ONE;
        loaders 0x004214EC, 0x0042152A) */
};

__attribute__((used, section(".rodata.bl006_pool_42156e")))
const struct open_cfw_bl006_pool_42156e open_cfw_bootloader_bl006_pool_42156e = {
    0x0000u, 0x400201BCu, 0x40021008u, 0x42004000u, 0x42006000u,
    0x42002000u
};
