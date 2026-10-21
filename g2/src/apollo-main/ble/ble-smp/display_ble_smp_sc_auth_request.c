/* Native Cordio smpScAuthReq 0x5e2aba. Its 24-byte event overlays the
 * incoming ARM stack; only authenticated fields are written. */
#include <stdint.h>

extern void DmSmpCbackExec(void *event); /* selected 0x4d24a8 */
extern void smpSmExecute(uint8_t *ccb, const uint8_t *event); /* selected 0x56ee62 */

void audio_ble_smp_sc_auth_request_body(uint8_t *ccb, uint8_t first,
                                         uint8_t second, uint8_t *frame)
{
    const uint32_t sc = *(const uint32_t *)(const void *)(ccb + 0x48u);
    const uint8_t *context = (const uint8_t *)(uintptr_t)sc;
    const uint8_t connection = ccb[0x3du];
    frame[0] = connection;
    frame[1] = 0u;
    if ((context[0] == 0u && (ccb[0x40u] & 4u) != 0u) ||
        (context[0] != 0u && context[1] == 2u)) {
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

__attribute__((naked)) void audio_ble_smp_sc_callback_5e2aba(uint8_t *ccb __attribute__((unused)),
                                                                uint8_t first __attribute__((unused)),
                                                                uint8_t second __attribute__((unused)))
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "sub sp, #24\n"
        "mov r3, sp\n"
        "bl audio_ble_smp_sc_auth_request_body\n"
        "add sp, #24\n"
        "pop {r7, pc}\n");
}
