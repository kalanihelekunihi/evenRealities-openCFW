/* BLE central peer manager, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\ble\app_ble_peer_mgr.c.
 * Native 0x4d8f4c..0x4d910a (findConnIdByAddr .. AppBleMasterPeerMgrUnpairDev),
 * literal pool 0x4d910c..0x4d914a. AppMasterSecClearAddr 0x4d8ff6 is already in
 * ble/ble-master/display_ble_master_security_clear.c.
 *
 * The "security address" record at RAM 0x200003d8 holds the six-byte address
 * of the device being unpaired plus its device type at +6 (0xff = none). */
#include <stdint.h>
#include <stddef.h>

/* Application connection control blocks at RAM 0x200717b0 (three 0x30-byte rows). */
typedef struct {
    uint8_t reserved0[4];
    uint8_t conn_id;        /* +4, 0 = slot free */
    uint8_t reserved5[0x2b];
} g2_app_conn_cb_t;
_Static_assert(sizeof(g2_app_conn_cb_t) == 0x30u, "app connection block");
#define PEER_MGR_CONN_SLOTS 3

typedef struct {
    uint8_t bytes[8];
} g2_bd_addr8_t;

extern uint8_t audio_ble_discovery_connection_records_200717b0[]; /* RAM 0x200717b0 */
extern volatile uint8_t audio_ble_master_security_address[7];    /* RAM 0x200003d8 */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern const uint8_t *DmConnPeerAddr(uint8_t conn_id);                         /* 0x4b6eea */
extern uint32_t audio_ble_privacy_compare_address(const uint8_t *a, const uint8_t *b); /* BdaCmp 0x4d294a */
extern uint8_t auth_state_clear_wrapper(void);                                 /* 0x4a22e8 */
extern uint8_t auth_mode_set(uint8_t mode);                                    /* 0x4a2168 */
extern void APP_MasterResetRetryConnectCnt(void);                              /* 0x4a2300 */
extern void APP_MasterConnectEvent(void);                                      /* 0x4a1b60, delayed callback */
extern void APP_MasterSysStartTryConnectRing(void);                            /* 0x4a23ac, delayed callback */
extern void APP_MasterSetTargetAddrName(const uint8_t *address, const char *name, uint8_t name_length); /* 0x4a2068 */
extern void APP_MasterUnpairDevEvent(const void *device);                      /* 0x4a1f38 */
extern void APP_MasterUnpairConnIdEvent(uint8_t conn_id);                      /* 0x4a1fc4 */
extern uint32_t fw_event_loop_remove_delayed(void (*callback)(void));          /* 0x476ace */

static const char module_tag[] = "ble.mgr"; /* ROM 0x78c9ec */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_peer_mgr.c"; /* ROM 0x6fff4c */
static const char fn_find[] = "findConnIdByAddr";               /* ROM 0x77dc2c */
static const char fn_unpair[] = "AppBleMasterPeerMgrUnpairDev"; /* ROM 0x75db10 */
static const char empty_name[] = "";                            /* literal-pool zero word 0x4d910c */
/* ROM 0x78c9f4: wildcard target address ff:ff:ff:ff:ff:ff plus two pad bytes. */
static const g2_bd_addr8_t wildcard_address = {{0xffu, 0xffu, 0xffu, 0xffu, 0xffu, 0xffu, 0x00u, 0x00u}};

#define PEER_LOG(level, fn, line, mask, fmt, ...) do { \
    if (audio_log_flags() & 2u) \
        audio_log_extended((level), module_tag, source_file, (fn), (line), fmt, ##__VA_ARGS__); \
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) \
        (void)compress_log_output((mask), "[ble.mgr]" fmt, "[ble.mgr]" fmt, ##__VA_ARGS__); \
} while (0)

/* Returns the connection id whose peer address equals addr, 0 if none.
 * Stock logs the peer address before its NULL check. */
uint8_t findConnIdByAddr(const uint8_t *addr)
{
    g2_app_conn_cb_t *rows = (g2_app_conn_cb_t *)(void *)audio_ble_discovery_connection_records_200717b0;
    for (int32_t i = 0; i < PEER_MGR_CONN_SLOTS; i++) {
        g2_app_conn_cb_t *row = &rows[i];
        if (row->conn_id == 0u)
            continue;
        const uint8_t *peer = DmConnPeerAddr(row->conn_id);
        PEER_LOG(4u, fn_find, 0x1eu, 0x11800000u, "Peer Address  : %02X:%02X:%02X:%02X:%02X:%02X",
                 peer[5], peer[4], peer[3], peer[2], peer[1], peer[0]);
        if (peer != NULL && audio_ble_privacy_compare_address(peer, addr) != 0u)
            return row->conn_id;
    }
    return 0u;
}

const uint8_t *AppMasterSecGetAddr(void)
{
    return (const uint8_t *)audio_ble_master_security_address;
}

/* Record the device to unpair; close its link first if one is connected or
 * opening, otherwise reset the central target and unpair immediately. */
void AppBleMasterPeerMgrUnpairDev(uint8_t dev_type, const uint8_t *address)
{
    if (address == NULL)
        return;
    (void)audio_queue_copy_bytes((void *)audio_ble_master_security_address, address, 6u);
    audio_ble_master_security_address[6] = dev_type;

    uint8_t conn_id = auth_state_clear_wrapper();
    if (conn_id == 0u)
        conn_id = findConnIdByAddr(address);

    if (conn_id != 0u) {
        PEER_LOG(3u, fn_unpair, 0x44u, 0x0c400000u,
                 "Device is connected or opening (connId=%d), will close before unpairing.", conn_id);
        APP_MasterResetRetryConnectCnt();
        (void)fw_event_loop_remove_delayed(APP_MasterConnectEvent);
        APP_MasterUnpairConnIdEvent(conn_id);
        return;
    }

    PEER_LOG(3u, fn_unpair, 0x4bu, 0x0c000000u, "Device not connected, unpairing immediately.");
    (void)auth_mode_set(0u);
    APP_MasterResetRetryConnectCnt();
    (void)fw_event_loop_remove_delayed(APP_MasterConnectEvent);
    (void)fw_event_loop_remove_delayed(APP_MasterSysStartTryConnectRing);
    g2_bd_addr8_t target = wildcard_address;
    APP_MasterSetTargetAddrName(target.bytes, empty_name, 0u);
    APP_MasterUnpairDevEvent((const void *)audio_ble_master_security_address);
}
