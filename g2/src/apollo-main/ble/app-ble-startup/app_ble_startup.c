/* BLE application startup and Cordio stack callbacks, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\ble\app_ble.c.
 * Native bleDmCback 0x4b748c, bleAttCback 0x4b74f0, bleCccCback 0x4b7532,
 * bleDelayedStartCback 0x4b758a, bleStackRegister 0x4b7ec2,
 * APP_BleAddressGet 0x4b80ea, appBleStart 0x4b80f0; literal pools
 * 0x4b7f60, 0x4b81fc, 0x4b8734..0x4b87a3.
 *
 * DM/ATT/CCC callbacks run in the Cordio handler that raised the event; each
 * copies the event (and any variable-length data) into a WSF message for the
 * application handler whose id is byte +0x56 of the BLE comm state
 * (_bleCommHandler 0x4b7d32, bleProcMsg 0x4b75ce). Other functions of this
 * stock file live in ble/ble-comm, ble/ble-stack and ble/ble-subsystem. */
#include <stdint.h>
#include <stddef.h>

/* Cordio wsfMsgHdr_t. */
typedef struct {
    uint16_t param; /* +0 connection id */
    uint8_t event;  /* +2 */
    uint8_t status; /* +3 */
} ble_wsf_msg_hdr_t;

/* Head of Cordio dmEvt_t for DM_SCAN_REPORT_IND (hciLeAdvReportEvt_t). */
typedef struct {
    ble_wsf_msg_hdr_t hdr; /* +0 */
    uint8_t *pData;        /* +4 advertising data */
    uint8_t len;           /* +8 */
} ble_dm_scan_report_head_t;

/* Cordio attEvt_t. */
typedef struct {
    ble_wsf_msg_hdr_t hdr; /* +0x0 */
    uint8_t *pValue;       /* +0x4 */
    uint16_t valueLen;     /* +0x8 */
    uint16_t handle;       /* +0xa */
    uint8_t continuing;    /* +0xc */
    uint8_t pad;           /* +0xd */
    uint16_t mtu;          /* +0xe */
} ble_att_evt_t;
_Static_assert(sizeof(ble_att_evt_t) == 16u, "attEvt_t");

/* Cordio attsCccEvt_t. */
typedef struct {
    ble_wsf_msg_hdr_t hdr; /* +0 */
    uint16_t handle;       /* +4 */
    uint16_t value;        /* +6 */
    uint8_t idx;           /* +8 */
    uint8_t pad;           /* +9 */
} ble_atts_ccc_evt_t;
_Static_assert(sizeof(ble_atts_ccc_evt_t) == 10u, "attsCccEvt_t");

#define BLE_DM_SCAN_REPORT_IND 0x26u   /* DM event carrying pData/len */
#define BLE_APP_DELAYED_START_EVT 0xbcu
#define BLE_CCC_SET_COUNT 6u

extern uint8_t audio_ble_comm_state[];   /* RAM 0x200727f0; +0x56 app handler id */
extern uint8_t audio_ble_comm_mode[];    /* RAM 0x200737b0; +0x0f BLE address bytes */
/* attsCccSet_t[6] {handle, valueRange, secLevel}: {0x0013 indicate},
 * {0x0825,0x0845,0x0865,0x0885,0x08a5 notify}, all security level 0. */
extern const uint8_t g2_ble_ccc_set_table[]; /* ROM 0x7518c0 */

/* WSF / Cordio. */
extern void *WsfMsgAlloc(uint16_t length);                    /* 0x4bf99e */
extern void WsfMsgSend(uint8_t handler, void *message);       /* 0x4bf9ba */
extern uint16_t DmSizeOfEvt(const void *event);               /* 0x4d2acc */
extern void DmRegister(void (*cback)(const void *));          /* 0x4d29ce */
extern void DmConnRegister(uint8_t client, void (*cback)(const void *)); /* 0x4b6c64 */
extern void AttRegister(void (*cback)(const void *));         /* 0x4b519e */
extern void AttConnRegister(void (*cback)(const void *));     /* 0x4b51c8 */
extern void AttsCccRegister(uint8_t count, const void *set,
                            void (*cback)(const void *));     /* 0x52c224 */
extern void GattSetSvcChangedIdx(uint8_t idx);                /* 0x4b5a3a */
extern void DmDevReset(void);                                 /* 0x4b3026 */
extern void vendorCcbInitLike(void);                          /* 0x4b73e8 */
extern void audio_ble_hci_driver_radio_shutdown(void);        /* HciDrvRadioShutdown 0x4b49ce */
extern uint32_t HciDrvRadioBoot(uint8_t with_identifier);     /* 0x4b48a6 */
extern void audio_ble_exactle_stack_initialize(void);         /* _bleExactleStackInit 0x4b7f64 */

/* ATT connection callback and service registration (no TSV row). */
extern void ble_att_conn_cback_5345aa(const void *event);
extern void app_disc_register_532e7c(void (*cback)(uint8_t, uint8_t)); /* AppDiscRegister */
extern void svc_core_gatt_cback_register_52dc1c(void *read_cback, void *write_cback);
extern void svc_core_add_group_52dbf0(void);
extern void svc_dis_add_group_53618c(void);
extern void svc_ota_cback_register_5361c6(void *read_cback, void *write_cback);
extern void svc_ota_add_group_5361bc(void);
extern void svc_eus_cback_register_5361de(void *read_cback, void *write_cback);
extern void svc_eus_add_group_5361d4(void);
extern void svc_ess_cback_register_5361f6(void *read_cback, void *write_cback);
extern void svc_ess_add_group_5361ec(void);
extern void svc_efs_cback_register_53620e(void *read_cback, void *write_cback);
extern void svc_efs_add_group_536204(void);
extern void svc_nus_cback_register_536226(void *read_cback, void *write_cback);
extern void svc_nus_add_group_53621c(void);

/* GATT callbacks registered by bleStackRegister. */
extern void APP_BleServerDiscCback(uint8_t conn, uint8_t status); /* 0x5355e0 */
extern uint8_t GattReadCback(void);       /* 0x4b5adc */
extern uint8_t GattWriteCback(void);      /* 0x4b5b02 */
extern uint8_t APP_EvenOtaWriteCback(void); /* 0x4bdc9c */
extern uint8_t eusWriteCallback(void);    /* 0x4bdf3c */
extern uint8_t essWriteCallback(void);    /* 0x4be2b4 */
extern uint8_t efsWriteCallback(void);    /* 0x4be486 */
extern uint8_t nusWriteCallback(void);    /* 0x4be7d2 */

/* Pairing records and helpers. */
extern uint8_t *audio_ble_pair_record(uint8_t conn);                  /* 0x4bb07c */
extern uint8_t audio_ble_connection_is_active_4bad26(uint8_t conn);   /* 0x4bad26 */
extern void audio_ble_pair_record_ccc_set_47b3e2(uint8_t *record, uint16_t idx,
                                                  uint16_t value);    /* 0x47b3e2 */

/* Product helpers. */
extern void audio_uart_checksum_copy(void *destination, const void *source, uint32_t length); /* memcpy 0x439be4 */
extern void g2_norflash_delay_us_491102(uint32_t microseconds);       /* 0x491102 */
extern uint32_t audio_event_loop_remove_delayed(void (*callback)(void)); /* 0x476ace */
extern void audio_event_loop_push_delayed(void (*callback)(void), uint32_t argument,
                                          uint32_t delay);            /* 0x47697e */

void bleDmCback(const void *event);
void bleAttCback(const void *event);
void bleCccCback(const void *event);
void bleDelayedStartCback(void);
void bleStackRegister(void);
uint8_t *APP_BleAddressGet(void);
void appBleStart(void);

static uint8_t ble_app_handler_id(void)
{
    return audio_ble_comm_state[0x56u];
}

/* 0x4b748c: scan reports carry their advertising data after the event. */
void bleDmCback(const void *event)
{
    const ble_dm_scan_report_head_t *evt = (const ble_dm_scan_report_head_t *)event;
    uint16_t length = DmSizeOfEvt(event);
    uint16_t report_length;
    ble_dm_scan_report_head_t *msg;

    if (evt->hdr.event == BLE_DM_SCAN_REPORT_IND)
        report_length = evt->len;
    else
        report_length = 0u;
    msg = (ble_dm_scan_report_head_t *)WsfMsgAlloc((uint16_t)(report_length + length));
    if (msg == NULL)
        return;
    audio_uart_checksum_copy(msg, evt, length);
    if (evt->hdr.event == BLE_DM_SCAN_REPORT_IND) {
        msg->pData = (uint8_t *)msg + length;
        audio_uart_checksum_copy(msg->pData, evt->pData, report_length);
    }
    WsfMsgSend(ble_app_handler_id(), msg);
}

/* 0x4b74f0 */
void bleAttCback(const void *event)
{
    const ble_att_evt_t *evt = (const ble_att_evt_t *)event;
    ble_att_evt_t *msg = (ble_att_evt_t *)WsfMsgAlloc((uint16_t)(evt->valueLen + sizeof(ble_att_evt_t)));

    if (msg == NULL)
        return;
    audio_uart_checksum_copy(msg, evt, sizeof(ble_att_evt_t));
    msg->pValue = (uint8_t *)(msg + 1);
    audio_uart_checksum_copy(msg->pValue, evt->pValue, evt->valueLen);
    WsfMsgSend(ble_app_handler_id(), msg);
}

/* 0x4b7532: a non-zero CCC handle on an active, bonded link is first stored
 * in the pairing record, then the event is forwarded. */
void bleCccCback(const void *event)
{
    const ble_atts_ccc_evt_t *evt = (const ble_atts_ccc_evt_t *)event;
    uint8_t *record;
    void *msg;

    if (evt->handle != 0u) {
        record = audio_ble_pair_record((uint8_t)evt->hdr.param);
        if (record != NULL && audio_ble_connection_is_active_4bad26((uint8_t)evt->hdr.param) != 0u)
            audio_ble_pair_record_ccc_set_47b3e2(record, evt->idx, evt->value);
    }
    msg = WsfMsgAlloc(sizeof(ble_atts_ccc_evt_t));
    if (msg == NULL)
        return;
    audio_uart_checksum_copy(msg, evt, sizeof(ble_atts_ccc_evt_t));
    WsfMsgSend(ble_app_handler_id(), msg);
}

/* 0x4b758a: re-armed every 10 s (20 s after an allocation failure); posts
 * app event 0xBC. Only the event byte of the 12-byte message is written. */
void bleDelayedStartCback(void)
{
    ble_wsf_msg_hdr_t *msg;

    (void)audio_event_loop_remove_delayed(bleDelayedStartCback);
    msg = (ble_wsf_msg_hdr_t *)WsfMsgAlloc(12u);
    if (msg == NULL) {
        audio_event_loop_push_delayed(bleDelayedStartCback, 0u, 20000u);
        return;
    }
    msg->event = BLE_APP_DELAYED_START_EVT;
    WsfMsgSend(ble_app_handler_id(), msg);
    audio_event_loop_push_delayed(bleDelayedStartCback, 0u, 10000u);
}

/* 0x4b7ec2: DM client 3 is DM_CLIENT_ID_APP. Five product GATT services
 * (Even OTA, EUS, ESS, EFS, NUS) register write callbacks only. */
void bleStackRegister(void)
{
    DmRegister(bleDmCback);
    DmConnRegister(3u, bleDmCback);
    AttRegister(bleAttCback);
    AttConnRegister(ble_att_conn_cback_5345aa);
    AttsCccRegister(BLE_CCC_SET_COUNT, g2_ble_ccc_set_table, bleCccCback);
    app_disc_register_532e7c(APP_BleServerDiscCback);
    svc_core_gatt_cback_register_52dc1c((void *)GattReadCback, (void *)GattWriteCback);
    svc_core_add_group_52dbf0();
    svc_dis_add_group_53618c();
    svc_ota_cback_register_5361c6(NULL, (void *)APP_EvenOtaWriteCback);
    svc_ota_add_group_5361bc();
    svc_eus_cback_register_5361de(NULL, (void *)eusWriteCallback);
    svc_eus_add_group_5361d4();
    svc_ess_cback_register_5361f6(NULL, (void *)essWriteCallback);
    svc_ess_add_group_5361ec();
    svc_efs_cback_register_53620e(NULL, (void *)efsWriteCallback);
    svc_efs_add_group_536204();
    svc_nus_cback_register_536226(NULL, (void *)nusWriteCallback);
    svc_nus_add_group_53621c();
    GattSetSvcChangedIdx(0u);
}

/* 0x4b80ea */
uint8_t *APP_BleAddressGet(void)
{
    return audio_ble_comm_mode + 0x0fu; /* RAM 0x200737bf */
}

/* 0x4b80f0: power-cycle the EM9305 (shutdown, 100 us, boot without
 * identifier), bring up the Cordio stack, then arm the delayed start. */
void appBleStart(void)
{
    vendorCcbInitLike();
    audio_ble_hci_driver_radio_shutdown();
    g2_norflash_delay_us_491102(100u);
    (void)HciDrvRadioBoot(0u);
    audio_ble_exactle_stack_initialize();
    bleStackRegister();
    DmDevReset();
    audio_event_loop_push_delayed(bleDelayedStartCback, 0u, 10000u);
}
