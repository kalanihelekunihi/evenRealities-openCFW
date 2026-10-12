/* Native Cordio smpScProcPairing 0x5e2784. The event overlaps the native
 * saved-R2/R3 entry frame, retaining ambient bytes outside explicit writes. */
#include <stdint.h>

extern uint8_t audio_ble_smp_handler_state[]; /* selected 0x20070aec */
extern const uint8_t *audio_ble_comm_registration_slot; /* live pSmpCfg 0x200004b8 */
extern uint8_t SmpScAllocScratchBuffers(void *ccb); /* selected 0x56cdc0 */
extern uint8_t *DmSecGetEccKey(void); /* selected 0x53490c */
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t); /* selected 0x439be4 */
extern void smpSmExecute(uint8_t *ccb, const uint8_t *event); /* selected 0x56ee62 */

static uint8_t *sc_of(uint8_t *ccb)
{
    uint32_t p;
    __builtin_memcpy(&p, ccb + 0x48u, sizeof(p));
    return (uint8_t *)(uintptr_t)p;
}

static uint8_t *sc_pointer(uint8_t *sc, uint32_t offset)
{
    uint32_t p;
    __builtin_memcpy(&p, sc + offset, sizeof(p));
    return (uint8_t *)(uintptr_t)p;
}

static void event_start(uint8_t *event, uint8_t connection)
{
    event[0] = connection;
    event[1] = 0u;
}

static void fail_pairing(uint8_t *ccb, uint8_t *event, uint8_t reason)
{
    event_start(event, ccb[0x3du]);
    event[2] = 3u;
    event[3] = reason;
    smpSmExecute(ccb, event);
}

uint32_t audio_ble_smp_sc_handler_body(uint8_t *ccb, uint8_t *mitm,
                                        uint8_t *passkey, uint8_t *event)
{
    uint8_t just_works = 1u;
    *passkey = 0u;
    *mitm = 0u;
    if ((ccb[0x23u] & 8u) && (ccb[0x2au] & 8u)) {
        if (ccb[0x22u] == 1u || ccb[0x29u] == 1u) {
            *mitm = 1u;
            just_works = 0u;
        }
    } else if (ccb[0x22u] == 1u && ccb[0x29u] == 1u) {
        *mitm = 1u;
        just_works = 0u;
    }
    if (*mitm == 0u && ((ccb[0x23u] | ccb[0x2au]) & 4u) &&
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

    if ((ccb[0x23u] & 8u) && (ccb[0x2au] & 8u)) {
        if (audio_ble_smp_handler_state[0xf8u] == 0u) {
            fail_pairing(ccb, event, 3u);
            return 0u;
        }
        uint8_t *sc = sc_of(ccb);
        sc[0] = 1u;
        sc[1] = 1u;
        sc[4] = *passkey;
        if (*mitm != 0u) {
            sc[1] = 2u;
        } else if (!just_works) {
            sc[1] = 3u;
            if (ccb[0x28u] == 4u &&
                (ccb[0x21u] == 1u || ccb[0x21u] == 4u))
                sc[1] = 4u;
            else if (ccb[0x28u] == 1u && ccb[0x21u] == 4u)
                sc[1] = 4u;
            else if ((ccb[0x23u] & 0x10u) && (ccb[0x2au] & 0x10u))
                sc[2] = 1u;
        } else if (ccb[0x28u] == 1u && ccb[0x21u] == 1u) {
            sc[1] = 4u;
            just_works = 0u;
        } else if (ccb[0x28u] == 3u || ccb[0x21u] == 3u) {
            just_works = 0u;
        }
        event_start(event, ccb[0x3du]);
        if (SmpScAllocScratchBuffers(ccb) == 0u) {
            event[2] = 3u;
            event[3] = 8u;
        } else {
            uint8_t *key = DmSecGetEccKey();
            (void)audio_queue_copy_bytes(sc_pointer(sc, 0x0cu), key, 0x20u);
            key = DmSecGetEccKey();
            (void)audio_queue_copy_bytes(sc_pointer(sc, 0x0cu) + 0x20u, key + 0x20u, 0x20u);
            key = DmSecGetEccKey();
            (void)audio_queue_copy_bytes(sc_pointer(sc, 0x10u), key + 0x40u, 0x20u);
            event[2] = 0x11u;
        }
        smpSmExecute(ccb, event);
    } else {
        const uint8_t *cfg = audio_ble_comm_registration_slot;
        if (cfg[8] & 8u) {
            fail_pairing(ccb, event, 3u);
            return 0u;
        }
        sc_of(ccb)[0] = 0u;
        event_start(event, ccb[0x3du]);
        event[2] = 0x12u;
        smpSmExecute(ccb, event);
    }

    if (just_works)
        ccb[0x40u] = (ccb[0x23u] & ccb[0x2au]) & 0xfbu;
    else
        ccb[0x40u] = (ccb[0x23u] & ccb[0x2au]) | 4u;
    uint8_t auth = ccb[0x3au] == 0u ? ccb[0x2au] : ccb[0x23u];
    const uint8_t *cfg = audio_ble_comm_registration_slot;
    if (just_works && (auth & cfg[8] & 4u)) {
        fail_pairing(ccb, event, 3u);
        return 0u;
    }
    if (ccb[0x24u] < cfg[5] || ccb[0x2bu] < cfg[5]) {
        fail_pairing(ccb, event, 6u);
        return 0u;
    }
    return 1u;
}

__attribute__((naked)) uint64_t audio_ble_smp_sc_handler_5e2784(uint8_t *ccb __attribute__((unused)),
                                                                    uint8_t *mitm __attribute__((unused)),
                                                                    uint8_t *passkey __attribute__((unused)))
{
    __asm__ volatile(
        "push {r2, r3, r4, r5, r6, lr}\n"
        "mov r3, sp\n"
        "bl audio_ble_smp_sc_handler_body\n"
        "pop {r1, r2, r4, r5, r6, pc}\n");
}
