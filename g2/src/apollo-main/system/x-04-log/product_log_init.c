/* Product logger bring-up, native 0x5bf964..0x5bf972 (UART text sink) and
 * 0x5bf9f6..0x5bfa5c (init-table entry, ROM 0x6d1e24, priority 1; its pool
 * words are 0x5bfa68/0x5bfa6c, while 0x5bfa5c..0x5bfa67 belong to the BLE
 * sink 0x5bf972 in system/log/logger-ble). No source path is retained. The
 * init table refers to the entry as g2_init_entry_5bf9f6 (manifest defsym).
 *
 * EasyLogger calls (elog_init 0x43d144, elog_set_fmt 0x43d33c,
 * elog_set_filter_lvl 0x43d3a6, elog_start 0x43d19a) bind to the upstream
 * elog.c unit. The async back end is the G2 elog_async_api.c glue. */
#include <stdint.h>
#include <stddef.h>

/* EasyLogger (upstream elog.c @a596b264). */
extern int elog_init(void); /* ElogErrCode, result ignored */
extern void elog_set_fmt(uint8_t level, size_t set);
extern void elog_set_filter_lvl(uint8_t level);
extern void elog_start(void);

/* elog_async_api.c glue. */
extern void elog_async_thread_init_448f44(void);
extern void g2_log_transport_initialize(void); /* 0x448c74 */
extern uint32_t elog_async_output_sink_set_448cac(uint32_t enabled, void *output);
extern uint32_t audio_uart_logger_descriptor_set_448cb8(uint32_t enabled, void *callback);
extern void elog_async_default_level_set_448cc4(uint8_t level);

extern uint32_t audio_uart_logger_ble_handler_5bf972(const uint8_t *message, uint32_t length);
extern void crash_record_init_47da58(void);
extern void shell_write_5415b4(const uint8_t *data, uint32_t len);

#define ELOG_LVL_ASSERT 0u
#define ELOG_LVL_ERROR 1u
#define ELOG_LVL_WARN 2u
#define ELOG_LVL_INFO 3u
#define ELOG_LVL_DEBUG 4u
#define ELOG_LVL_VERBOSE 5u
#define ELOG_FMT_ALL 0xffu
/* ELOG_FMT_LVL | ELOG_FMT_TAG | ELOG_FMT_TIME | ELOG_FMT_LINE */
#define ELOG_FMT_PRODUCT 0x87u

/* UART sink of the async log consumer: raw write to the debug UART shell. */
uint32_t elog_uart_output_5bf964(const uint8_t *text, uint32_t length)
{
    shell_write_5415b4(text, length);
    return length;
}

int32_t product_log_init_5bf9f6(void)
{
    (void)elog_init();
    elog_set_fmt(ELOG_LVL_ASSERT, ELOG_FMT_ALL);
    elog_set_fmt(ELOG_LVL_ERROR, ELOG_FMT_PRODUCT);
    elog_set_fmt(ELOG_LVL_WARN, ELOG_FMT_PRODUCT);
    elog_set_fmt(ELOG_LVL_INFO, ELOG_FMT_PRODUCT);
    elog_set_fmt(ELOG_LVL_DEBUG, ELOG_FMT_PRODUCT);
    elog_set_fmt(ELOG_LVL_VERBOSE, ELOG_FMT_PRODUCT);
    elog_async_thread_init_448f44();
    g2_log_transport_initialize();
    (void)elog_async_output_sink_set_448cac(1u, (void *)elog_uart_output_5bf964);
    (void)audio_uart_logger_descriptor_set_448cb8(0u, (void *)audio_uart_logger_ble_handler_5bf972);
    elog_async_default_level_set_448cc4(1u);
    crash_record_init_47da58();
    elog_set_filter_lvl(ELOG_LVL_INFO);
    elog_start();
    return 0;
}
