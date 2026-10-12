/* Native Cordio legacy smpAuthReq 0x56e84c with its 24-byte ARM event frame. */
#include <stdint.h>
extern void DmSmpCbackExec(void *event);
extern void smpSmExecute(uint8_t *ccb, const uint8_t *event);

void audio_ble_smp_auth_request_body(uint8_t *ccb, uint8_t first,
                                      uint8_t second, uint8_t *frame)
{
    frame[0] = ccb[0x3du];
    frame[1] = 0u;
    if (ccb[0x40u] & 4u) {
        frame[2] = 0x2eu;
        frame[4] = first;
        frame[5] = second;
        DmSmpCbackExec(frame);
    } else {
        frame[2] = 4u;
        frame[4] = 0u;
        frame[5] = 0u;
        frame[6] = 0u;
        frame[20] = 3u;
        smpSmExecute(ccb, frame);
    }
}

__attribute__((naked)) void audio_ble_smp_auth_callback_56e84c(uint8_t *ccb __attribute__((unused)),
                                                                   uint8_t first __attribute__((unused)),
                                                                   uint8_t second __attribute__((unused)))
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "sub sp, #24\n"
        "mov r3, sp\n"
        "bl audio_ble_smp_auth_request_body\n"
        "add sp, #24\n"
        "pop {r7, pc}\n");
}
