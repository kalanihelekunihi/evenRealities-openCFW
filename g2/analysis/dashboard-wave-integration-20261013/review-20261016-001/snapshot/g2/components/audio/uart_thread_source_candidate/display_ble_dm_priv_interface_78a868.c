/* Cordio privacy interface 0x78a868, dispatch 0x76af6c, native 0x4d254c..0x4d27ce.
 * Uses the 26-byte dmPrivCb overlay and dmCb offsets measured in the pinned image. */
#include <stddef.h>
#include <stdint.h>

extern uint8_t audio_ble_dm_priv_cb_storage[26u];
extern uint8_t audio_ble_dm_handler_state[];
extern void *memcpy(void *, const void *, size_t);
extern void *memset(void *, int, size_t);
extern uint8_t SecAes(uint8_t *, uint8_t *, uint8_t, uint16_t, uint8_t);
extern void SecRand(uint8_t *, uint8_t);
extern void HciLeAddDeviceToResolvingListCmd(uint8_t, const uint8_t *, const uint8_t *, const uint8_t *);
extern void HciLeRemoveDeviceFromResolvingList(uint8_t, const uint8_t *);
extern void HciLeClearResolvingList(void);
extern void HciLeSetAddrResolutionEnable(uint8_t);
extern void HciLeSetPrivacyModeCmd(uint8_t, uint8_t *, uint8_t);
extern void dmDevPassEvtToDevPriv(uint8_t, uint8_t, uint8_t, uint8_t);

typedef void (*audio_ble_dm_event_callback)(void *);
typedef void (*audio_ble_dm_priv_fn)(void *);
static uint16_t rd16(const uint8_t *p) { return *(const uint16_t *)(const void *)p; }
static void callback(void *message) {
    (*(audio_ble_dm_event_callback *)(void *)(audio_ble_dm_handler_state + 8u))(message);
}
static void set_addr_resolution(uint8_t enabled) {
    audio_ble_dm_priv_cb_storage[9u] = enabled;
    HciLeSetAddrResolutionEnable(enabled);
}

static void resolve_addr(void *message_ptr) {
    uint8_t *const m = (uint8_t *)message_ptr;
    uint8_t *const p = audio_ble_dm_priv_cb_storage;
    if ((p[3u] & 1u) == 0u) {
        uint8_t plain[16];
        (void)memcpy(p, m + 20u, 3u);
        (void)memcpy(plain, m + 23u, 3u);
        (void)memset(plain + 3u, 0, 13u);
        p[3u] |= 1u;
        (void)SecAes(m + 4u, plain, audio_ble_dm_handler_state[12u], rd16(m), 0x78u);
    } else {
        m[3u] = 7u;
        m[2u] = 0x37u;
        callback(m);
    }
}
static void add_device(void *message_ptr) {
    const uint8_t *const m = (const uint8_t *)message_ptr;
    uint8_t *const p = audio_ble_dm_priv_cb_storage;
    p[8u] = m[43u];
    *(uint16_t *)(void *)(p + 4u) = rd16(m);
    HciLeAddDeviceToResolvingListCmd(m[4u], m + 5u, m + 11u, m + 27u);
}
static void remove_device(void *message_ptr) {
    const uint8_t *const m = (const uint8_t *)message_ptr;
    *(uint16_t *)(void *)(audio_ble_dm_priv_cb_storage + 6u) = rd16(m);
    HciLeRemoveDeviceFromResolvingList(m[4u], m + 5u);
}
static void clear_list(void *message_ptr) {
    (void)message_ptr;
    HciLeClearResolvingList();
}
static void set_enable(void *message_ptr) {
    const uint8_t *const m = (const uint8_t *)message_ptr;
    set_addr_resolution(m[4u]);
}
static void set_privacy_mode(void *message_ptr) {
    uint8_t *const m = (uint8_t *)message_ptr;
    HciLeSetPrivacyModeCmd(m[4u], m + 5u, m[11u]);
}
static void generate_addr(void *message_ptr) {
    uint8_t *const m = (uint8_t *)message_ptr;
    uint8_t *const p = audio_ble_dm_priv_cb_storage;
    if ((p[3u] & 2u) == 0u) {
        SecRand(p + 10u, 3u);
        p[12u] = (uint8_t)((p[12u] & 0x3fu) | 0x40u);
        (void)memset(p + 13u, 0, 13u);
        p[3u] |= 2u;
        (void)SecAes(m + 4u, p + 10u, audio_ble_dm_handler_state[12u], rd16(m), 0x79u);
    } else {
        m[3u] = 7u;
        m[2u] = 0x38u;
        callback(m);
    }
}

const audio_ble_dm_priv_fn audio_ble_dm_priv_actions[7]
    __attribute__((used, aligned(4))) = {
        resolve_addr, add_device, remove_device, clear_list,
        set_enable, set_privacy_mode, generate_addr,
    };

void audio_ble_dm_priv_reset_4d27c0(void) {
    audio_ble_dm_priv_cb_storage[3u] = 0u;
    audio_ble_dm_handler_state[22u] = 0u;
}
void audio_ble_dm_priv_msg_handler_4d27ae(void *message_ptr) {
    const uint8_t *const m = (const uint8_t *)message_ptr;
    audio_ble_dm_priv_actions[m[2u] & 7u](message_ptr);
}
void audio_ble_dm_priv_hci_handler_4d26e8(void *event_ptr) {
    uint8_t *const e = (uint8_t *)event_ptr;
    uint8_t *const p = audio_ble_dm_priv_cb_storage;
    uint8_t *const dm = audio_ble_dm_handler_state;
    switch (e[2u]) {
    case 0x15u:
        e[2u] = 0x3au;
        *(uint16_t *)(void *)e = *(uint16_t *)(void *)(p + 4u);
        if (e[3u] == 0u && p[8u] != 0u && dm[22u] == 0u) set_addr_resolution(1u);
        break;
    case 0x16u:
        e[2u] = 0x3bu;
        *(uint16_t *)(void *)e = *(uint16_t *)(void *)(p + 6u);
        break;
    case 0x17u:
        e[2u] = 0x3cu;
        if (e[3u] == 0u && dm[22u] != 0u) set_addr_resolution(0u);
        break;
    case 0x18u: e[2u] = 0x3du; break;
    case 0x19u: e[2u] = 0x3eu; break;
    case 0x1au:
        e[2u] = 0x3fu;
        if (e[3u] == 0u) {
            dm[22u] = p[9u];
            const uint8_t enabled = dm[22u] != 0u;
            dmDevPassEvtToDevPriv(enabled ? 0x0du : 0x0cu, enabled, 0u, 0u);
        }
        break;
    default: return;
    }
    callback(e);
}

const audio_ble_dm_priv_fn audio_ble_dm_priv_table_a[3]
    __attribute__((used, aligned(4))) = {
        (audio_ble_dm_priv_fn)audio_ble_dm_priv_reset_4d27c0,
        audio_ble_dm_priv_hci_handler_4d26e8,
        audio_ble_dm_priv_msg_handler_4d27ae,
    };
