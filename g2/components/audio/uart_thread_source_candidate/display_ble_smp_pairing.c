/* Native Cordio legacy smpProcPairing 0x56e6e0. The native saved-R2/R3
 * entry frame supplies the event's ambient bytes. */
#include <stdint.h>
extern const uint8_t *audio_ble_comm_registration_slot; /* live pSmpCfg */
extern void smpSmExecute(uint8_t *ccb, const uint8_t *event);

static void fail(uint8_t *ccb, uint8_t *event, uint8_t reason)
{
    event[0] = ccb[0x3du];
    event[1] = 0u;
    event[2] = 3u;
    event[3] = reason;
    smpSmExecute(ccb, event);
}

uint32_t audio_ble_smp_legacy_pairing_body(uint8_t *ccb, uint8_t *mitm,
                                            uint8_t *passkey, uint8_t *event)
{
    uint8_t just_works = 1u;
    *passkey = 0u;
    *mitm = 0u;
    if (ccb[0x22u] == 1u && ccb[0x29u] == 1u) {
        *mitm = 1u;
        just_works = 0u;
    } else if (((ccb[0x23u] | ccb[0x2au]) & 4u) &&
               ccb[0x21u] != 3u && ccb[0x28u] != 3u &&
               ((ccb[0x21u] != 0u && ccb[0x21u] != 1u) ||
                (ccb[0x28u] != 0u && ccb[0x28u] != 1u))) {
        just_works = 0u;
        uint8_t pass = (ccb[0x21u] == 0u || ccb[0x21u] == 1u ||
                        (ccb[0x21u] == 4u &&
                         (ccb[0x28u] == 2u || ccb[0x28u] == 4u))) ? 1u : 0u;
        if (ccb[0x28u] != 2u || ccb[0x21u] != 2u)
            pass ^= ccb[0x3au] == 0u ? 1u : 0u;
        *passkey = pass;
    }
    if (just_works)
        ccb[0x40u] = (ccb[0x23u] & ccb[0x2au]) & 0xfbu;
    else
        ccb[0x40u] = (ccb[0x23u] & ccb[0x2au]) | 4u;
    const uint8_t auth = ccb[0x3au] == 0u ? ccb[0x2au] : ccb[0x23u];
    const uint8_t *cfg = audio_ble_comm_registration_slot;
    if (just_works && (auth & cfg[8] & 4u)) {
        fail(ccb, event, 3u);
        return 0u;
    }
    if (ccb[0x24u] < cfg[5] || ccb[0x2bu] < cfg[5]) {
        fail(ccb, event, 6u);
        return 0u;
    }
    return 1u;
}

__attribute__((naked)) uint64_t audio_ble_smp_pairing_callback_56e6e0(uint8_t *ccb __attribute__((unused)),
                                                                           uint8_t *mitm __attribute__((unused)),
                                                                           uint8_t *passkey __attribute__((unused)))
{
    __asm__ volatile(
        "push {r2, r3, r4, lr}\n"
        "mov r3, sp\n"
        "bl audio_ble_smp_legacy_pairing_body\n"
        "pop {r1, r2, r4, pc}\n");
}
