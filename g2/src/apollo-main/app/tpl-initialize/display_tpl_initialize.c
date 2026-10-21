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

void audio_tpl_initialize_body(uint32_t service, uint32_t *saved)
{
    uint8_t *row = audio_tpl_service_table + ((uint8_t)service * 20u);
    row[0] = (uint8_t)service;
    __builtin_memcpy(row + 4u, &saved[0], 4u);
    __builtin_memcpy(row + 8u, &saved[1], 4u);
    __builtin_memcpy(row + 12u, &saved[2], 4u);
    __builtin_memcpy(row + 16u, &saved[8], 4u);
    audio_uart_buffer_zero(audio_tpl_contexts, 0xe0u, 0u);
    if (audio_tpl_send_mutex != 0) return;
    audio_tpl_send_mutex = audio_uart_mutex_new(0);
    if (audio_tpl_send_mutex == 0) {
        if (audio_log_level() & 2u) {
            saved[0] = 0x62u;
            saved[1] = (uint32_t)(uintptr_t)failure;
            audio_log_extended(1u, module, source, function, 0x62u, failure);
        }
        if ((audio_log_level() & 1u) || (audio_log_level() & 4u))
            (void)compressed_log_output(0x04000000u, failure_short, failure_short);
    } else {
        if (audio_log_level() & 2u) {
            saved[0] = 0x64u;
            saved[1] = (uint32_t)(uintptr_t)success;
            audio_log_extended(4u, module, source, function, 0x64u, success);
        }
        if ((audio_log_level() & 1u) || (audio_log_level() & 4u))
            (void)compressed_log_output(0x10000000u, success_short, success_short);
    }
}

__attribute__((naked)) uint64_t TPL_Init(uint8_t service __attribute__((unused)), ...)
{
    __asm__ volatile(
        "push {r1, r2, r3, r4, r5, r6, r7, lr}\n"
        "mov r1, sp\n"
        "bl audio_tpl_initialize_body\n"
        "pop {r0, r1, r2, r4, r5, r6, r7, pc}\n");
}
