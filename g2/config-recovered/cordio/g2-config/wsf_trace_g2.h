/*
 * G2 product WSF trace dispatch, recovered from firmware 2.2.6.10.
 *
 * Force-include this header (after cordio_recovered_config.h) when compiling
 * Cordio host sources for Apollo main.  It includes the AmbiqSuite R3.2.0
 * port wsf_trace.h (which keeps its subsystem macros: DM/L2C/ATT/EATT/SMP/APP
 * INFO/WARN/ERR, DM ALLOC/FREE, WSF WARN/ERR) and then replaces the four
 * WSF_TRACEn back ends with the product cascade that every stock Cordio trace
 * site inlines.
 *
 * Stock evidence (identical shape at every site checked):
 *   dmConnCmplStates 0x4B5B24 ("dmConnCmplStates %d", DM INFO),
 *   dmConnCcbAlloc 0x4B5C78 (DM ALLOC/ERR), attsProcMtuReq 0x56C6FC (ATT WARN),
 *   SmpHandler 0x537D0C (SMP WARN "AES token mismatch: %d %d").
 * Each site:
 *   - while the elog gate 0x4C9C50 (byte 0x2007502F) is set, picks elog level
 *     1/2/3/4 by comparing the level label with "ERR"/"WARN"/"INFO" through the
 *     bounded compare 0x44B610 (3/4/4 characters), and emits
 *     elog(level, subsys, file, function, line, msg, ...) when bit 1 of the
 *     log-flags byte (getter 0x43D0CE, byte 0x20004543) is set;
 *   - otherwise calls WsfTrace 0x52A63C(label, msg, ...) unless the subsystem
 *     tag is "HCI" (the HCI test re-reads the gate, which is then clear).
 * The gate is re-read before every comparison, as in stock.
 *
 * Differences that remain: the stock file argument is the IAR build path
 * (D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\...); define
 * G2_CORDIO_STOCK_FILE per unit to reproduce it, otherwise __FILE__ is used.
 * __LINE__ follows the pinned file, not the product-modified stock file
 * (stock lines are a few lines later, e.g. dmConnCmplStates 155 vs 152).
 */
#ifndef OPENCFW_G2_WSF_TRACE_G2_H
#define OPENCFW_G2_WSF_TRACE_G2_H

#include "wsf_types.h"
#include "wsf_trace.h"

extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);                /* 0x4C9C50 */
extern int32_t audio_l2c_strncmp(const char *a, const char *b, uint32_t count); /* 0x44B610 */
extern uint32_t platform_log_flags(void);                                      /* 0x43D0CE */
extern void audio_log_extended(uint8_t level, const char *module, const char *file,
                               const char *function, uint32_t line, const char *format, ...);

#ifndef G2_CORDIO_STOCK_FILE
#define G2_CORDIO_STOCK_FILE __FILE__
#endif

#define G2_WSF_TRACE_ELOG(level, subsys, ...)                                                     \
  do {                                                                                            \
    if ((platform_log_flags() & 2u) != 0u)                                                        \
      audio_log_extended((level), (subsys), G2_CORDIO_STOCK_FILE, __func__, __LINE__, __VA_ARGS__); \
  } while (0)

#define G2_WSF_TRACE(subsys, stat, ...)                                                           \
  do {                                                                                            \
    if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u && audio_l2c_strncmp((stat), "ERR", 3u) == 0)  \
      G2_WSF_TRACE_ELOG(1u, (subsys), __VA_ARGS__);                                               \
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u && audio_l2c_strncmp((stat), "WARN", 4u) == 0) \
      G2_WSF_TRACE_ELOG(2u, (subsys), __VA_ARGS__);                                               \
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u && audio_l2c_strncmp((stat), "INFO", 4u) == 0) \
      G2_WSF_TRACE_ELOG(3u, (subsys), __VA_ARGS__);                                               \
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u)                                     \
      G2_WSF_TRACE_ELOG(4u, (subsys), __VA_ARGS__);                                               \
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u || audio_l2c_strncmp((subsys), "HCI", 3u) != 0) \
      WsfTrace((stat), __VA_ARGS__);                                                              \
  } while (0)

#undef WSF_TRACE0
#undef WSF_TRACE1
#undef WSF_TRACE2
#undef WSF_TRACE3
#define WSF_TRACE0(subsys, stat, msg)                   G2_WSF_TRACE(subsys, stat, msg)
#define WSF_TRACE1(subsys, stat, msg, var1)             G2_WSF_TRACE(subsys, stat, msg, var1)
#define WSF_TRACE2(subsys, stat, msg, var1, var2)       G2_WSF_TRACE(subsys, stat, msg, var1, var2)
#define WSF_TRACE3(subsys, stat, msg, var1, var2, var3) G2_WSF_TRACE(subsys, stat, msg, var1, var2, var3)

#endif /* OPENCFW_G2_WSF_TRACE_G2_H */
