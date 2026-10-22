/* BLE application storage (S1 storage-definition pass, 2.2.6.10).
 *
 * Stock owners: platform\ble\profiles\ancc\profile_ancc.c and
 * platform\ble\profiles\ring\profile_ring.c (service UUIDs, characteristic
 * descriptors and discovery lists), the product discovery / startup / central
 * modules (CCC tables, connection spec, central cells), the BLE threads
 * (production, WSF, msgrx, msgtx: contexts, control blocks, stacks and
 * osThreadAttr_t records), the product slave configuration and the Ambiq
 * HCI radio driver buffers.
 *
 * Cordio-owned objects (dmConnCb, dmCb, dmScanCb, attsCb, attsCsfCb,
 * attsSignCb, SMP_ScCcb, appDb, pAppMasterCfg, pAppSecCfg, attGattSvcUuid,
 * gattDiscCharList) are not defined here; attCliChCfgUuid is referenced by
 * its Cordio name (att_uuid.c, ROM 0x78f540 in the stock image).
 *
 * .data values are from the decoded 0x20000000 init stream (scatter record
 * 0x75d3f4); ROM bytes are copied from ota_s200_firmware_ota.bin
 * (VA = file offset + 0x437fe0). */
#include <stdint.h>

/* Cordio attcDiscChar_t / attcDiscCfg_t / attsCccSet_t / hciConnSpec_t. */
typedef struct {
    const uint8_t *uuid; /* +0 */
    uint8_t settings;    /* +4 ATTC_SET_* */
} g2_attc_disc_char_t;
_Static_assert(sizeof(g2_attc_disc_char_t) == 8u, "attcDiscChar_t");

typedef struct {
    const uint8_t *value; /* +0 */
    uint8_t value_len;    /* +4 */
    uint8_t hdl_idx;      /* +5 */
} g2_attc_disc_cfg_t;
_Static_assert(sizeof(g2_attc_disc_cfg_t) == 8u, "attcDiscCfg_t");

typedef struct {
    uint16_t handle;
    uint16_t value_range;
    uint8_t sec_level;
} g2_atts_ccc_set_t;
_Static_assert(sizeof(g2_atts_ccc_set_t) == 6u, "attsCccSet_t");

typedef struct {
    uint16_t conn_interval_min;
    uint16_t conn_interval_max;
    uint16_t conn_latency;
    uint16_t sup_timeout;
    uint16_t min_ce_len;
    uint16_t max_ce_len;
} g2_hci_conn_spec_data_t;
_Static_assert(sizeof(g2_hci_conn_spec_data_t) == 12u, "hciConnSpec_t");

typedef struct {
    const char *name;
    uint32_t attr_bits;
    void *cb_mem;
    uint32_t cb_size;
    void *stack_mem;
    uint32_t stack_size;
    int32_t priority;
    uint32_t tz_module;
    uint32_t reserved;
} g2_os_thread_attr_data_t;
_Static_assert(sizeof(g2_os_thread_attr_data_t) == 36u, "osThreadAttr_t");

extern const uint8_t attCliChCfgUuid[2]; /* Cordio att_uuid.c, 0x2902 */

/* ---- profile_ancc.c ----------------------------------------------------- */

/* ROM 0x787fc0: ANCS 7905F431-B5CE-4E99-A40F-4B1E122D00D0 (little-endian). */
const uint8_t g2_ancs_service_uuid[16] = {
    0xd0u, 0x00u, 0x2du, 0x12u, 0x1eu, 0x4bu, 0x0fu, 0xa4u,
    0x99u, 0x4eu, 0xceu, 0xb5u, 0x31u, 0xf4u, 0x05u, 0x79u,
};
/* ROM 0x787fd0 / 0x787fe0 / 0x787ff0: notification source, control point,
 * data source. */
static const uint8_t g2_ancs_notif_src_uuid[16] = {
    0xbdu, 0x1du, 0xa2u, 0x99u, 0xe6u, 0x25u, 0x58u, 0x8cu,
    0xd9u, 0x42u, 0x01u, 0x63u, 0x0du, 0x12u, 0xbfu, 0x9fu,
};
static const uint8_t g2_ancs_ctrl_pt_uuid[16] = {
    0xd9u, 0xd9u, 0xaau, 0xfdu, 0xbdu, 0x9bu, 0x21u, 0x98u,
    0xa8u, 0x49u, 0xe1u, 0x45u, 0xf3u, 0xd8u, 0xd1u, 0x69u,
};
static const uint8_t g2_ancs_data_src_uuid[16] = {
    0xfbu, 0x7bu, 0x7cu, 0xceu, 0x6au, 0xb3u, 0x44u, 0xbeu,
    0xb5u, 0x4bu, 0xd6u, 0x24u, 0xe9u, 0xc6u, 0xeau, 0x22u,
};
/* ROM 0x78df94..0x78dfbb: five attcDiscChar_t descriptors. */
static const g2_attc_disc_char_t g2_ancc_notif_src_char = {g2_ancs_notif_src_uuid, 3u};
static const g2_attc_disc_char_t g2_ancc_notif_src_ccc = {attCliChCfgUuid, 6u};
static const g2_attc_disc_char_t g2_ancc_ctrl_pt_char = {g2_ancs_ctrl_pt_uuid, 3u};
static const g2_attc_disc_char_t g2_ancc_data_src_char = {g2_ancs_data_src_uuid, 3u};
static const g2_attc_disc_char_t g2_ancc_data_src_ccc = {attCliChCfgUuid, 6u};

/* RAM 0x200030bc (.data): 0x78df94 0x78df9c 0x78dfa4 0x78dfac 0x78dfb4. */
void *g2_ancc_disc_char_list[5] = {
    (void *)&g2_ancc_notif_src_char,
    (void *)&g2_ancc_notif_src_ccc,
    (void *)&g2_ancc_ctrl_pt_char,
    (void *)&g2_ancc_data_src_char,
    (void *)&g2_ancc_data_src_ccc,
};

/* ---- profile_ring.c ----------------------------------------------------- */

/* ROM 0x7880b0: BAE80001-4F05-4503-8E65-3AF1F7329D1F (little-endian). */
const uint8_t g2_ring_service_uuid[16] = {
    0x1fu, 0x9du, 0x32u, 0xf7u, 0xf1u, 0x3au, 0x65u, 0x8eu,
    0x03u, 0x45u, 0x05u, 0x4fu, 0x01u, 0x00u, 0xe8u, 0xbau,
};
/* ROM 0x7880c0 / 0x7880d0: BAE80010 / BAE80011 characteristics. */
static const uint8_t g2_ring_char_10_uuid[16] = {
    0x1fu, 0x9du, 0x32u, 0xf7u, 0xf1u, 0x3au, 0x65u, 0x8eu,
    0x03u, 0x45u, 0x05u, 0x4fu, 0x10u, 0x00u, 0xe8u, 0xbau,
};
static const uint8_t g2_ring_char_11_uuid[16] = {
    0x1fu, 0x9du, 0x32u, 0xf7u, 0xf1u, 0x3au, 0x65u, 0x8eu,
    0x03u, 0x45u, 0x05u, 0x4fu, 0x11u, 0x00u, 0xe8u, 0xbau,
};
/* ROM 0x78dfcc..0x78dfe3. */
static const g2_attc_disc_char_t g2_ring_char_10 = {g2_ring_char_10_uuid, 3u};
static const g2_attc_disc_char_t g2_ring_char_11 = {g2_ring_char_11_uuid, 3u};
static const g2_attc_disc_char_t g2_ring_char_11_ccc = {attCliChCfgUuid, 6u};

/* RAM 0x200030d8 (.data): 0x78dfcc 0x78dfd4 0x78dfdc. */
void *g2_ring_disc_char_list[3] = {
    (void *)&g2_ring_char_10,
    (void *)&g2_ring_char_11,
    (void *)&g2_ring_char_11_ccc,
};

/* ---- app discovery (attcDiscCfg_t lists) -------------------------------- */

/* ROM 0x78f532 {02 00} indicate, 0x78f534 {01 00} notify, 0x7682af {03}. */
static const uint8_t g2_disc_ccc_indicate[2] = {0x02u, 0x00u};
static const uint8_t g2_disc_ccc_notify[2] = {0x01u, 0x00u};
static const uint8_t g2_disc_value_03[1] = {0x03u};

/* ROM 0x784dc0: master list. */
const g2_attc_disc_cfg_t g2_disc_cfg_list_master[2] = {
    {g2_disc_ccc_indicate, 2u, 1u},
    {g2_disc_ccc_notify, 2u, 4u},
};
/* ROM 0x75daf0: slave list. */
const g2_attc_disc_cfg_t g2_disc_cfg_list_slave[4] = {
    {g2_disc_ccc_indicate, 2u, 1u},
    {g2_disc_value_03, 1u, 2u},
    {g2_disc_ccc_notify, 2u, 4u},
    {g2_disc_ccc_notify, 2u, 7u},
};

/* ---- app_ble_startup.c -------------------------------------------------- */

/* ROM 0x7518c0: attsCccSet_t[6]; 0x0013 indicate, 0x0825..0x08a5 notify. */
const g2_atts_ccc_set_t g2_ble_ccc_set_table[6] = {
    {0x0013u, 0x0002u, 0u},
    {0x0825u, 0x0001u, 0u},
    {0x0845u, 0x0001u, 0u},
    {0x0865u, 0x0001u, 0u},
    {0x0885u, 0x0001u, 0u},
    {0x08a5u, 0x0001u, 0u},
};

/* ---- product slave configuration ---------------------------------------- */

/* ROM 0x78f6d2: appSlaveCfg_t {connMax = 1}. */
const uint8_t audio_ble_slave_profile_table[1] = {1u};

/* ---- central (app_ble_central_*.c) -------------------------------------- */

/* ROM 0x78a04c: 20..40 ms interval (0x10/0x20), latency 0, 6 s timeout. */
const g2_hci_conn_spec_data_t g2_ble_master_conn_spec_78a04c = {
    0x0010u, 0x0020u, 0x0000u, 0x0258u, 0x0000u, 0x0000u,
};
uint8_t *g2_ble_master_conn_ccb;               /* RAM 0x200742f8, row of 0x200717b0 */
uint32_t g2_ble_master_short_interval_tick;    /* RAM 0x2007430c */
uint8_t g2_ble_master_scan_filter_20074f81;    /* RAM 0x20074f81 */

/* ---- BLE threads -------------------------------------------------------- */

typedef struct {
    void (*init)(void);   /* +0x00 */
    void (*deinit)(void); /* +0x04 */
    void *thread;         /* +0x08 */
    void *queue;          /* +0x0c */
    uint32_t reserved_10;
    uint32_t reserved_14;
    void *pool;           /* +0x18 */
    uint32_t reserved_1c;
    uint32_t reserved_20;
} g2_ble_production_context_data_t;
_Static_assert(sizeof(g2_ble_production_context_data_t) == 0x24u, "thread context stride");

extern void threadBleProductionInit(void);   /* 0x5383be */
extern void threadBleProductionDeinit(void); /* 0x5383ea */

/* RAM 0x20004044 (.data): {0x5383bf, 0x5383eb, 0...}, thread-manager slot 11. */
g2_ble_production_context_data_t g2_ble_production_context = {
    threadBleProductionInit, threadBleProductionDeinit, 0, 0, 0u, 0u, 0, 0u, 0u,
};
__attribute__((aligned(8))) uint8_t g2_ble_production_thread_cb[0x70];      /* RAM 0x200723e0 */
__attribute__((aligned(8))) uint8_t g2_ble_production_thread_stack[0x1000]; /* RAM 0x2036de40 (SSRAM) */

/* RAM 0x20076540: above the zero-init end 0x20075048 (stock no-init area). */
__attribute__((aligned(8))) uint8_t g2_ble_wsf_thread_cb[0x70];
__attribute__((aligned(8))) uint8_t g2_ble_wsf_thread_stack[0x4000];        /* RAM 0x20045498 */

/* ble_msgrx / ble_msgtx: control blocks, stacks and their osThreadAttr_t. */
__attribute__((aligned(8))) static uint8_t g2_ble_msgrx_thread_cb[0x70];      /* RAM 0x20072220 */
__attribute__((aligned(8))) static uint8_t g2_ble_msgrx_thread_stack[0x4000]; /* RAM 0x2004ba98 */
__attribute__((aligned(8))) static uint8_t g2_ble_msgtx_thread_cb[0x70];      /* RAM 0x200721b0 */
__attribute__((aligned(8))) static uint8_t g2_ble_msgtx_thread_stack[0x4000]; /* RAM 0x20047a98 */
static const char g2_ble_msgrx_thread_name[] = "ble_msgrx"; /* ROM 0x78c5fc */
static const char g2_ble_msgtx_thread_name[] = "ble_msgtx"; /* ROM 0x78c5f0 */

/* ROM 0x75b880: priority 0x30 (osPriorityAboveNormal), TrustZone module 1. */
const g2_os_thread_attr_data_t g2_ble_msgrx_thread_attr = {
    g2_ble_msgrx_thread_name, 0u, g2_ble_msgrx_thread_cb, 0x70u,
    g2_ble_msgrx_thread_stack, 0x4000u, 0x30, 1u, 0u,
};
/* ROM 0x75b85c. */
const g2_os_thread_attr_data_t g2_ble_msgtx_thread_attr = {
    g2_ble_msgtx_thread_name, 0u, g2_ble_msgtx_thread_cb, 0x70u,
    g2_ble_msgtx_thread_stack, 0x4000u, 0x30, 1u, 0u,
};

/* ---- Ambiq HCI radio driver (HciDrvRadioBoot 0x4b48a6) ------------------- */

/* RAM 0x200703ec: transport command buffer handed over as {buffer, 0x40}
 * (0x40 words). */
__attribute__((aligned(4))) uint8_t audio_ble_hci_radio_boot_config[0x100];
/* RAM 0x20065a10: scheduler queue storage, 0x820 bytes of 0x104-byte items. */
__attribute__((aligned(4))) uint8_t audio_ble_hci_radio_scheduler_config[0x820];
