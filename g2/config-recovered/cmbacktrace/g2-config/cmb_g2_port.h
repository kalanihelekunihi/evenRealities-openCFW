/*
 * openCFW G2 CmBacktrace logging port (forced include, ahead of cmb_user_cfg.h).
 *
 * Evidence (G2 2.2.6.10 Apollo main): every cmb_println() site in the
 * CmBacktrace TU at 0x5939ae..0x5947af expands to four calls, in this order:
 *   crash-record printf 0x47da78 (fmt, ...), 0x47da78 ("\r\n" at ROM 0x5947b0),
 *   console printf 0x4733ee (fmt, ...),      0x4733ee ("\r\n").
 * See cm_backtrace_init 0x5939ae (0x593a0e..0x593a28) and
 * cm_backtrace_firmware_info 0x593a38. The two sinks are reconstructed as
 * crash_record_printf_47da78 (system/p-05-crash-record/crash_record.c) and
 * audio_ble_hci_boot_log_4733ee (AmbiqSuite am_util_stdio_printf slot).
 *
 * Linker-provided bounds (upstream GCC-path names). Stock literal pool
 * 0x594310..0x59432c: CSTACK 0x2007d000..0x20080000 (12 KiB main stack) and
 * .text 0x438400..0x5fa056; the G2 linker script must define _sstack/_estack
 * and _stext/_etext with those values (stock IAR resolved them through
 * __section_begin/__section_end("CSTACK"/".text")).
 */
#ifndef OPENCFW_G2_CMB_PORT_H
#define OPENCFW_G2_CMB_PORT_H

#ifndef __ASSEMBLER__
extern void crash_record_printf_47da78(const char *format, ...);
extern void audio_ble_hci_boot_log_4733ee(const char *format, ...);

#define OPENCFW_CMB_PRINTLN(...)                    \
    do {                                            \
        crash_record_printf_47da78(__VA_ARGS__);    \
        crash_record_printf_47da78("\r\n");         \
        audio_ble_hci_boot_log_4733ee(__VA_ARGS__); \
        audio_ble_hci_boot_log_4733ee("\r\n");      \
    } while (0)
#endif

#endif /* OPENCFW_G2_CMB_PORT_H */
