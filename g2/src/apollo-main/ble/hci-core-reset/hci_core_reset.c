/* Cordio HCI reset entry points, Ambiq dual-chip port (AmbiqSuite
 * third_party/cordio/ble-host/sources/hci/ambiq/{hci_core.c,hci_cmd.c} and
 * the EM9305 hci_vs file). Native HciResetSequence 0x52ac6a,
 * hciClearCmdQueue 0x52b664, HciResetCmd 0x52b682, hciCoreResetStart
 * 0x569b4a; literal pools 0x52ae14..0x52ae1b, 0x52b6b4..0x52b6bb.
 *
 * All four are Ambiq variants of Packetcraft r20.05c (pinned upstream):
 * - HciResetSequence also drains hciCb.rxQueue and releases every ACL
 *   connection slot (upstream only sets resetting and starts the sequence);
 * - HciResetCmd first sends HCI_HW_ERROR_CBACK_EVT to the security callback
 *   and flushes the command queue (upstream only sets numCmdPkts = 1);
 * - hciCoreResetStart follows HCI_Reset with HciVscUpdateBDAddress.
 * They match AmbiqSuite R3.2.0 (third-party/local-vendor, not tracked)
 * line for line, with HCI_TRACE_INFO0 compiled out. */
#include <stdint.h>
#include <stddef.h>

/* Cordio hciCoreConn_t, 3 rows (DM_CONN_MAX) at hciCoreCb + 0. */
typedef struct {
    uint8_t *pTxAclPkt;  /* +0x00 fragmenting TX packet */
    uint8_t *pNextTxFrag; /* +0x04 */
    uint8_t *pRxAclPkt;  /* +0x08 reassembling RX packet */
    uint8_t *pNextRxFrag; /* +0x0c */
    uint16_t handle;     /* +0x10 0xFFFF = free */
    uint16_t txAclRemLen; /* +0x12 */
    uint16_t rxAclRemLen; /* +0x14 */
    uint8_t fragmenting; /* +0x16 */
    uint8_t flowDisabled; /* +0x17 */
    uint8_t queuedBufs;  /* +0x18 */
    uint8_t outBufs;     /* +0x19 */
    uint8_t pad[2];      /* +0x1a */
} hci_core_conn_t;
_Static_assert(sizeof(hci_core_conn_t) == 0x1cu, "hciCoreConn_t stride");

/* Cordio hciHwErrorEvt_t. */
typedef struct {
    uint16_t param; /* +0 */
    uint8_t event;  /* +2 */
    uint8_t status; /* +3 */
    uint8_t code;   /* +4 */
} hci_hw_error_evt_t;

#define HCI_HANDLE_NONE 0xffffu
#define HCI_CONN_MAX 3u
#define HCI_HW_ERROR_CBACK_EVT 0x14u
#define HCI_OPCODE_RESET 0x0c03u
#define HCI_LEN_RESET 0u

/* hciCoreCb, RAM 0x20071478: conn[3] at +0, numSupAdvSets +0x91. */
extern uint8_t audio_ble_hci_controller_state_20071478[];
/* hciCb, RAM 0x20073870: rxQueue +0x00, secCback +0x0c, handlerId +0x20,
 * resetting +0x21. */
extern uint8_t audio_ble_hci_stack_state_20073870[];
/* hciCmdCb, RAM 0x20073a90: cmdTimer +0x00, cmdQueue +0x10, numCmdPkts +0x1a. */
extern uint8_t audio_ble_hci_cmd_state_20073a90[];

extern void *WsfMsgDeq(void *queue, uint8_t *handler_id); /* 0x4bf9ec */
extern void WsfMsgFree(void *message);                    /* 0x4bf9b0 */
extern uint8_t *hciCmdAlloc(uint16_t opcode, uint8_t length); /* 0x52ae38 */
extern void hciCmdSend(uint8_t *message);                 /* 0x52ae5e */
extern void audio_ble_hci_tx_ready(uint8_t bufs);         /* hciCoreTxReady 0x52a79e */
extern void HciVscUpdateBDAddress(void);                  /* 0x4b4d08 */

void HciResetSequence(void);
void hciClearCmdQueue(void);
void HciResetCmd(void);
void hciCoreResetStart(void);

/* 0x52ac6a */
void HciResetSequence(void)
{
    uint8_t *hci = audio_ble_hci_stack_state_20073870;
    hci_core_conn_t *conn = (hci_core_conn_t *)(void *)audio_ble_hci_controller_state_20071478;
    uint8_t handler_id;
    uint8_t *buf;
    uint8_t i;

    /* free any pending incoming packets */
    while ((buf = WsfMsgDeq(hci, &handler_id)) != NULL)
        WsfMsgFree(buf);

    for (i = HCI_CONN_MAX; i > 0u; i--, conn++) {
        if (conn->pTxAclPkt != NULL) {
            WsfMsgFree(conn->pTxAclPkt);
            conn->pTxAclPkt = NULL;
        }
        conn->fragmenting = 0u;
        if (conn->pRxAclPkt != NULL) {
            WsfMsgFree(conn->pRxAclPkt);
            conn->pRxAclPkt = NULL;
        }
        conn->handle = HCI_HANDLE_NONE;
        /* outstanding buffers are now available; service TX data path */
        audio_ble_hci_tx_ready(conn->outBufs);
    }

    hci[0x21u] = 1u; /* hciCb.resetting */
    hciCoreResetStart();
}

/* 0x52b664: free unsent commands; numCmdPkts = 1 for the reset command. */
void hciClearCmdQueue(void)
{
    uint8_t *cmd = audio_ble_hci_cmd_state_20073a90;
    uint8_t handler_id;
    uint8_t *buf;

    while ((buf = WsfMsgDeq(cmd + 0x10u, &handler_id)) != NULL)
        WsfMsgFree(buf);
    cmd[0x1au] = 1u;
}

/* 0x52b682: let the security module drop pending requests first. Only the
 * event byte of the stack event is initialised. */
void HciResetCmd(void)
{
    hci_hw_error_evt_t evt;
    void (*sec_cback)(void *event);
    uint8_t *buf;

    evt.event = HCI_HW_ERROR_CBACK_EVT;
    __builtin_memcpy(&sec_cback, audio_ble_hci_stack_state_20073870 + 0x0cu, sizeof sec_cback);
    sec_cback(&evt);

    hciClearCmdQueue();

    if ((buf = hciCmdAlloc(HCI_OPCODE_RESET, HCI_LEN_RESET)) != NULL)
        hciCmdSend(buf);
}

/* 0x569b4a */
void hciCoreResetStart(void)
{
    /* send an HCI Reset command to start the sequence */
    HciResetCmd();
    /* update Bluetooth address in the controller */
    HciVscUpdateBDAddress();
}
