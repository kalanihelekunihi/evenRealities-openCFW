/* Native TPL_Init 0x4b892c. Four 56-byte contexts are explicitly cleared;
 * service registration indices and the live transport vtable remain external. */
#include <stdint.h>

extern uint8_t audio_tpl_service_table[]; /* live 0x20071414; extent unproven */
uint8_t audio_tpl_contexts[4u * 56u]; /* source-owned 0x20070dc8 */
void *audio_tpl_send_mutex; /* source-owned pointer cell 0x20074b00 */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void *audio_uart_mutex_new(const void *);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "prot.tran";
static const char source[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\transport_protocol\\transport_protocol.c";
static const char function[] = "TPL_Init";
static const char failure[] = "Failed to create _g_SendBufferMutex";
static const char failure_short[] = "[prot.tran]Failed to create _g_SendBufferMutex";
static const char success[] = "Static send buffer mutex initialized";
static const char success_short[] = "[prot.tran]Static send buffer mutex initialized";

/* Callback slot type for the service row. The only caller (stock 0x4c94c8)
 * passes code addresses 0x464d1d, 0x48f12d, 0x4bdff5 and 0x4be14f (Thumb bit
 * set), so the four words are function pointers; their individual signatures
 * differ, so they are stored here as a generic code pointer. */
typedef void (*tpl_callback_fn)(void);

/* Stock 0x4B892C (TPL_Init). The fifth argument is the caller's first stack
 * word (sp[0] = APP_BleEusDirectSendDataMsg at stock 0x4c94c8). The stock
 * IAR epilogue popped two spilled argument words into R0:R1; the only caller
 * (thread_manager_resource_init_4c94c8) discards the result, so this returns 0. */
uint64_t TPL_Init(uint8_t service, tpl_callback_fn send_status, tpl_callback_fn rx_from_ble,
                  tpl_callback_fn send_data, tpl_callback_fn direct_send)
{
    uint8_t *row = audio_tpl_service_table + ((uint32_t)service * 20u);
    row[0] = service;
    __builtin_memcpy(row + 4u, &send_status, 4u);
    __builtin_memcpy(row + 8u, &rx_from_ble, 4u);
    __builtin_memcpy(row + 12u, &send_data, 4u);
    __builtin_memcpy(row + 16u, &direct_send, 4u);
    audio_uart_buffer_zero(audio_tpl_contexts, 0xe0u, 0u);
    if (audio_tpl_send_mutex != 0) return 0u;
    audio_tpl_send_mutex = audio_uart_mutex_new(0);
    if (audio_tpl_send_mutex == 0) {
        if (audio_log_level() & 2u) {
            audio_log_extended(1u, module, source, function, 0x62u, failure);
        }
        if ((audio_log_level() & 1u) || (audio_log_level() & 4u))
            (void)compressed_log_output(0x04000000u, failure_short, failure_short);
    } else {
        if (audio_log_level() & 2u) {
            audio_log_extended(4u, module, source, function, 0x64u, success);
        }
        if ((audio_log_level() & 1u) || (audio_log_level() & 4u))
            (void)compressed_log_output(0x10000000u, success_short, success_short);
    }
    return 0u;
}
