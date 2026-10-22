/* UI common API, stock D:\01_workspace\s200_ap510b_iar_git\app\gui\common\ui_common_api.c
 * (log tag "ui_common_api"). Native 0x509c1c..0x509f97; literal pool
 * 0x509f98..0x509fdb. Byte event FIFO (fifo_create / fifo_push / fifo_pop,
 * stock function names from the log records) plus three page helpers. */
#include <stdint.h>
#include <stddef.h>
#include "g2_ui_common_api.h"

extern void *file_heap_allocate(uint32_t size);                              /* 0x474cd2 */
extern void file_heap_free(void *buffer);                                    /* 0x474d16 */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);  /* memset 0x43c0e4 */
extern uint32_t audio_settings_unread_message_count(void);                   /* service_ancc_message_count_get 0x4974d4 */
extern uint32_t audio_settings_charge_percent(void);                         /* CHG_GetSoc 0x4ad8fa */
extern uint32_t audio_log_flags(void);                                       /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);                           /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "ui_common_api"; /* ROM 0x789cf0 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\common\\ui_common_api.c"; /* ROM 0x70797c */
static const char fn_create[] = "fifo_create"; /* ROM 0x78c800 */
static const char fn_push[] = "fifo_push";     /* ROM 0x78c80c */
static const char fn_pop[] = "fifo_pop";       /* ROM 0x78c818 */
static const char malloc_failed[] = "fifo malloc failed"; /* ROM 0x784720 */
static const char malloc_failed_short[] = "[ui_common_api]fifo malloc failed"; /* ROM 0x75c258 */
static const char fifo_null[] = "fifo is NULL"; /* ROM 0x789d00 */
static const char fifo_null_short[] = "[ui_common_api]fifo is NULL"; /* ROM 0x773d9c */
static const char data_null[] = "data is NULL or len is 0"; /* ROM 0x773db8 */
static const char data_null_short[] = "[ui_common_api]data is NULL or len is 0"; /* ROM 0x75066c */
static const char fifo_full[] = "fifo is full,free_space = %d,len = %d"; /* ROM 0x750694 */
static const char fifo_full_short[] = "[ui_common_api]fifo is full,free_space = %d,len = %d"; /* ROM 0x725140 */
static const char buffer_null[] = "buffer is NULL or max_len is 0"; /* ROM 0x767350 */
static const char buffer_null_short[] = "[ui_common_api]buffer is NULL or max_len is 0"; /* ROM 0x73a694 */
static const char fifo_empty[] = "fifo is empty"; /* ROM 0x789d10 */
static const char fifo_empty_short[] = "[ui_common_api]fifo is empty"; /* ROM 0x767370 */

/* Stock log macro expansion: full record when flag bit 1 is set, compressed
 * record when bit 0 or bit 2 is set. */
#define UI_LOG(level, fn, line, cflags, msg, msg_short, ...)                                        \
    do {                                                                                            \
        if ((audio_log_flags() & 2u) != 0u)                                                         \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (msg), ##__VA_ARGS__); \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                       \
            (void)compress_log_output((cflags), (msg_short), (msg_short), ##__VA_ARGS__);            \
    } while (0)

g2_ui_fifo_t *ui_common_api_fn_00509c1c(void)
{
    g2_ui_fifo_t *fifo = file_heap_allocate(sizeof(g2_ui_fifo_t));
    if (fifo == NULL) {
        UI_LOG(2u, fn_create, 0x1du, 0x08000000u, malloc_failed, malloc_failed_short);
        return NULL;
    }
    audio_uart_buffer_zero(fifo, sizeof(g2_ui_fifo_t), 0u);
    fifo->head = 0u;
    fifo->tail = 0u;
    fifo->count = 0u;
    return fifo;
}

void ui_common_api_fn_00509c96(g2_ui_fifo_t *fifo)
{
    if (fifo != NULL)
        file_heap_free(fifo);
}

/* All or nothing: refuses the whole record when it does not fit. */
int32_t ui_common_api_fn_00509ca2(g2_ui_fifo_t *fifo, const uint8_t *data, uint16_t len)
{
    if (fifo == NULL) {
        UI_LOG(2u, fn_push, 0x3fu, 0x08000000u, fifo_null, fifo_null_short);
        return -4;
    }
    if (data == NULL || len == 0u) {
        UI_LOG(2u, fn_push, 0x44u, 0x08000000u, data_null, data_null_short);
        return -3;
    }
    uint16_t free_space = (uint16_t)(G2_UI_FIFO_SIZE - fifo->count);
    if (free_space < len) {
        UI_LOG(2u, fn_push, 0x4bu, 0x08800000u, fifo_full, fifo_full_short, (uint32_t)free_space,
               (uint32_t)len);
        return -1;
    }
    for (uint16_t i = 0u; i < len; i++) {
        fifo->buf[fifo->head] = data[i];
        fifo->head = (uint16_t)((fifo->head + 1) % G2_UI_FIFO_SIZE);
        fifo->count++;
    }
    return 0;
}

int32_t ui_common_api_fn_00509dfa(const g2_ui_fifo_t *fifo)
{
    if (fifo == NULL)
        return -4;
    return fifo->count == 0u ? 1 : 0;
}

/* Returns the number of bytes copied (0 when empty). */
int32_t ui_common_api_fn_00509e14(g2_ui_fifo_t *fifo, uint8_t *buffer, uint16_t max_len)
{
    if (fifo == NULL) {
        UI_LOG(2u, fn_pop, 0x73u, 0x08000000u, fifo_null, fifo_null_short);
        return -4;
    }
    if (buffer == NULL || max_len == 0u) {
        UI_LOG(2u, fn_pop, 0x78u, 0x08000000u, buffer_null, buffer_null_short);
        return -3;
    }
    if (fifo->count == 0u) {
        UI_LOG(2u, fn_pop, 0x7du, 0x08000000u, fifo_empty, fifo_empty_short);
        return 0;
    }
    uint16_t n = max_len;
    if (n >= fifo->count)
        n = fifo->count;
    for (uint16_t i = 0u; i < n; i++) {
        buffer[i] = fifo->buf[fifo->tail];
        fifo->tail = (uint16_t)((fifo->tail + 1) % G2_UI_FIFO_SIZE);
        fifo->count--;
    }
    return (int32_t)n;
}

void ui_common_api_fn_00509f52(g2_ui_fifo_t *fifo)
{
    if (fifo != NULL) {
        fifo->head = 0u;
        fifo->tail = 0u;
        fifo->count = 0u;
        audio_uart_buffer_zero(fifo->buf, G2_UI_FIFO_SIZE, 0u);
    }
}

/* Page origin on the display: always (0, 0) on this product. */
int32_t ui_common_api_fn_00509f7a(int32_t *x, int32_t *y)
{
    *x = 0;
    *y = 0;
    return 0;
}

uint32_t ui_common_api_fn_00509f86(void)
{
    return audio_settings_unread_message_count();
}

uint8_t ui_common_api_fn_00509f8e(void)
{
    return (uint8_t)audio_settings_charge_percent();
}
