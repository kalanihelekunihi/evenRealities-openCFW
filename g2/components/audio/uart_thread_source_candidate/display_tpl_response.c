/* Native _tplReponse 0x4b9012. The response bytes are live transport RAM. */
#include <stdint.h>

extern uint8_t audio_tpl_response_buffer[]; /* stock 0x20004204, at least 8 bytes */
extern uint8_t audio_tpl_service_table[]; /* stock 0x20071414, live registration row */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "prot.tran";
static const char source[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\transport_protocol\\transport_protocol.c";
static const char function[] = "_tplReponse";
static const char pipe_error[] = "tx pipe error header.b.destinationID = %d error";
static const char pipe_error_short[] = "[prot.tran]tx pipe error header.b.destinationID = %d error";
static const char tx_error[] = "tx ret = %d error";
static const char tx_error_short[] = "[prot.tran]tx ret = %d error";

void audio_tpl_response_body(uint32_t pipe, uint32_t *saved)
{
    uint8_t *buffer = audio_tpl_response_buffer;
    buffer[2] = (uint8_t)saved[0];
    buffer[6] = (uint8_t)saved[1];
    buffer[7] = (uint8_t)((buffer[7] & 0xe1u) | ((saved[2] & 15u) << 1));
    uint8_t result = 0u;
    if ((uint8_t)pipe == 0u) {
        uint32_t callback;
        __builtin_memcpy(&callback, audio_tpl_service_table + 16u, 4u);
        if (callback != 0u)
            result = ((uint8_t (*)(uint8_t *, uint32_t))(uintptr_t)callback)(buffer, 8u);
    } else {
        if (audio_log_level() & 2u) {
            saved[0] = 0x16cu;
            saved[1] = (uint32_t)(uintptr_t)pipe_error;
            audio_log_extended(1u, module, source, function, 0x16cu, pipe_error,
                               (uint32_t)(buffer[1] >> 4));
        }
        if ((audio_log_level() & 1u) || (audio_log_level() & 4u))
            (void)compressed_log_output(0x04400000u, pipe_error_short,
                                        pipe_error_short, (uint32_t)(buffer[1] >> 4));
    }
    if (result != 0u) {
        if (audio_log_level() & 2u) {
            saved[0] = 0x171u;
            saved[1] = (uint32_t)(uintptr_t)tx_error;
            audio_log_extended(1u, module, source, function, 0x171u, tx_error,
                               (uint32_t)result);
        }
        if ((audio_log_level() & 1u) || (audio_log_level() & 4u))
            (void)compressed_log_output(0x04400000u, tx_error_short,
                                        tx_error_short, (uint32_t)result);
    }
}

/* IAR returns the original saved R1/R2 stack words as R0/R1. */
__attribute__((naked)) uint64_t audio_tpl_response(uint8_t pipe __attribute__((unused)), ...)
{
    __asm__ volatile(
        "push {r1, r2, r3, r4, r5, lr}\n"
        "mov r1, sp\n"
        "bl audio_tpl_response_body\n"
        "pop {r0, r1, r2, r4, r5, pc}\n");
}
