/* R1 Cordio host handlers needed by the Nordic BLE service adapter. */
#if defined(R1_CORDIO_RTC0)
#include <stdbool.h>

#include "att_api.h"
#include "att_handler.h"
#include "dm_api.h"
#include "dm_handler.h"
#include "hci_api.h"
#include "hci_defs.h"
#include "l2c_api.h"
#include "l2c_handler.h"
#include "sec_api.h"
#include "smp_api.h"
#include "smp_handler.h"
#include "wsf_os.h"
#include "wsf_assert.h"
#include "cordio_ble_event_bridge.h"
#include "cordio_host_bootstrap.h"
#include "r1_adv_bridge.h"
#include "r1_gap_service.h"
#include "r1_gatts_database_cordio.h"
#include "r1_gatts_api_bridge.h"
#include "r1_security_cordio.h"

enum { R1_ATT_MTU = 247, R1_RX_ACL_LEN = R1_ATT_MTU + 4 };
extern void *pvPortMalloc(size_t bytes);
extern void vPortFree(void *pointer);
_Static_assert(R1_RX_ACL_LEN == 251, "R1 ACL length includes L2CAP header");

static attCfg_t r1AttCfg;
static bool r1HostInitialized;
static uint8_t r1HostResetReady;
static uint8_t r1HostShutdownPending;
extern void r1_cordio_softdevice_reset_complete(void);

static void r1_cordio_reset_callback(dmEvt_t *event)
{
  if (event->hdr.event == DM_RESET_CMPL_IND && event->hdr.status == 0)
  {
    __atomic_store_n(&r1HostResetReady, 1u, __ATOMIC_RELEASE);
    if (__atomic_exchange_n(&r1HostShutdownPending, 0u,
                            __ATOMIC_ACQ_REL) != 0u)
      r1_cordio_softdevice_reset_complete();
  }
  else if (event->hdr.event == DM_ADV_START_IND)
  {
    r1_cordio_adv_started(event->hdr.status);
    if (event->hdr.status != 0u) WsfAssert(__FILE__, (uint16_t)__LINE__);
  }
  else if (event->hdr.event == DM_ADV_STOP_IND)
  {
    r1_cordio_adv_stopped(event->hdr.status);
    if (event->hdr.status != 0u) WsfAssert(__FILE__, (uint16_t)__LINE__);
  }
  else if (event->hdr.event == DM_SEC_PAIR_IND ||
           event->hdr.event == DM_SEC_PAIR_CMPL_IND ||
           event->hdr.event == DM_SEC_PAIR_FAIL_IND ||
           event->hdr.event == DM_SEC_KEY_IND ||
           event->hdr.event == DM_SEC_LTK_REQ_IND ||
           event->hdr.event == DM_SEC_ENCRYPT_IND ||
           event->hdr.event == DM_SEC_ENCRYPT_FAIL_IND)
  {
    if (!r1_cordio_security_dm_event(event))
      WsfAssert(__FILE__, (uint16_t)__LINE__);
  }
}

void r1_cordio_adv_event_overflow(void)
{
  WsfAssert(__FILE__, (uint16_t)__LINE__);
}

static void r1_cordio_connection_callback(dmEvt_t *event)
{
  bool published = true;
  switch (event->hdr.event)
  {
  case DM_CONN_OPEN_IND:
    if (event->connOpen.status == 0u)
    {
      r1_cordio_ccc_freeze();
      r1_cordio_ccc_new_connection(event->hdr.param);
      AttsCccInitTable(event->hdr.param, 0);
      published = r1_cordio_gap_connected(event->hdr.param,
                   event->connOpen.handle, event->connOpen.role,
                   event->connOpen.addrType, event->connOpen.peerAddr,
                   event->connOpen.connInterval, event->connOpen.connLatency,
                   event->connOpen.supTimeout);
    }
    break;
  case DM_CONN_CLOSE_IND:
    if (event->connClose.status == 0u)
    {
      r1_cordio_gatts_clear_pending(event->hdr.param);
      r1_cordio_gatts_tx_clear(event->hdr.param);
      r1_cordio_security_reset(event->hdr.param);
      published = r1_cordio_gap_disconnected(event->hdr.param,
                   event->connClose.handle, event->connClose.reason);
      r1_cordio_ccc_retain(event->hdr.param);
      AttsCccClearTable(event->hdr.param);
    }
    else if (event->connClose.status == HCI_ERR_ADV_TIMEOUT)
    {
      /* Legacy high-duty directed advertising reports its timeout as a
       * failed connection completion, not as DM_ADV_STOP_IND. */
      r1_cordio_adv_stopped(0u);
    }
    break;
  case DM_CONN_UPDATE_IND:
    if (event->connUpdate.status == 0u)
    {
      published = r1_cordio_gap_conn_updated(event->hdr.param,
                   event->connUpdate.handle, event->connUpdate.connInterval,
                   event->connUpdate.connLatency, event->connUpdate.supTimeout);
    }
    break;
  case DM_CONN_DATA_LEN_CHANGE_IND:
    published = r1_cordio_gap_data_length_updated(event->hdr.param,
                 event->dataLenChange.handle,
                 event->dataLenChange.maxTxOctets,
                 event->dataLenChange.maxTxTime,
                 event->dataLenChange.maxRxOctets,
                 event->dataLenChange.maxRxTime);
    break;
  case DM_PHY_UPDATE_IND:
    published = r1_cordio_gap_phy_updated(event->hdr.param,
                 event->phyUpdate.handle, event->phyUpdate.status,
                 event->phyUpdate.txPhy, event->phyUpdate.rxPhy);
    break;
  default:
    /* Security and ATT events require separate adapters. */
    break;
  }
  if (!published)
  {
    /* A dropped connection event invalidates the Nordic application's link
     * state. Make this failure observable even with WSF assertions disabled. */
    WsfAssert(__FILE__, (uint16_t)__LINE__);
  }
}

static void r1_cordio_att_callback(attEvt_t *event)
{
  bool published = true;
  if (event->hdr.event == ATT_MTU_UPDATE_IND)
    published = r1_cordio_att_mtu_updated(event->hdr.param, event->mtu);
  else if (event->hdr.event == ATTC_READ_RSP ||
           event->hdr.event == ATTC_READ_LONG_RSP ||
           event->hdr.event == ATTC_READ_BY_TYPE_RSP)
    published = r1_cordio_att_read_response(event->hdr.param,
                 event->hdr.event == ATTC_READ_BY_TYPE_RSP ? 2u : 1u,
                 event->hdr.status, event->handle,
                 event->pValue, event->valueLen);
  else if (event->hdr.event == ATTS_HANDLE_VALUE_CNF)
    published = r1_cordio_gatts_tx_complete(event->hdr.param,
                                             event->handle,
                                             event->hdr.status);
  if (!published)
  {
    WsfAssert(__FILE__, (uint16_t)__LINE__);
  }
  /* Write and notification events need the remaining GATT data adapter. */
}

bool r1_cordio_host_ready(void)
{
  return __atomic_load_n(&r1HostResetReady, __ATOMIC_ACQUIRE) != 0u;
}

void r1_cordio_host_request_shutdown(void)
{
  __atomic_store_n(&r1HostResetReady, 0u, __ATOMIC_RELEASE);
  __atomic_store_n(&r1HostShutdownPending, 1u, __ATOMIC_RELEASE);
  DmDevReset();
}

void r1_cordio_dm_disconnect(uint8_t conn_id, uint8_t reason)
{
  DmConnClose(DM_CLIENT_ID_APP, conn_id, reason);
}

void r1_cordio_dm_set_data_length(uint8_t conn_id, uint16_t tx_octets,
                                  uint16_t tx_time)
{
  DmConnSetDataLen(conn_id, tx_octets, tx_time);
}

void r1_cordio_dm_conn_param_update(uint8_t conn_id, uint16_t min_interval,
                                    uint16_t max_interval, uint16_t latency,
                                    uint16_t timeout)
{
  hciConnSpec_t spec = {0};
  spec.connIntervalMin = min_interval;
  spec.connIntervalMax = max_interval;
  spec.connLatency = latency;
  spec.supTimeout = timeout;
  DmConnUpdate(conn_id, &spec);
}

void r1_cordio_dm_set_phy(uint8_t conn_id, uint8_t all_phys,
                          uint8_t tx_phys, uint8_t rx_phys)
{
  DmSetPhy(conn_id, all_phys, tx_phys, rx_phys, 0u);
}

void r1_cordio_att_mtu_request(uint8_t conn_id, uint16_t mtu)
{
  AttcMtuReq(conn_id, mtu);
}

void r1_cordio_att_read_request(uint8_t conn_id, uint16_t handle,
                                uint16_t offset)
{
  if (offset == 0u) AttcReadReq(conn_id, handle);
  else AttcReadLongReq(conn_id, handle, offset, FALSE);
}

void r1_cordio_att_read_by_type_request(uint8_t conn_id, uint16_t first,
                                        uint16_t last, uint16_t uuid)
{
  uint8_t little_endian_uuid[2] = {(uint8_t)uuid, (uint8_t)(uuid >> 8)};
  AttcReadByTypeReq(conn_id, first, last, sizeof(little_endian_uuid),
                    little_endian_uuid, FALSE);
}

void r1_cordio_host_bootstrap(void)
{
  if (r1HostInitialized)
  {
    return;
  }

  /* HCI was registered by the controller bootstrap. Preserve its handler
   * while installing the peripheral host's security and protocol owners. */
  SecInit();
  SecAesInit();
  SecCmacInit();
  SecEccInit();

  HciSetMaxRxAclLen(R1_RX_ACL_LEN);
  r1AttCfg = *pAttCfg;
  r1AttCfg.mtu = R1_ATT_MTU;
  pAttCfg = &r1AttCfg;

  DmDevVsInit(0);
  DmAdvInit();
  DmConnInit();
  DmConnSlaveInit();
  DmPhyInit();
  DmSecInit();
  DmHandlerInit(WsfOsSetNextHandler(DmHandler));

  L2cSlaveHandlerInit(WsfOsSetNextHandler(L2cSlaveHandler));
  L2cInit();
  L2cSlaveInit();

  AttHandlerInit(WsfOsSetNextHandler(AttHandler));
  AttsInit();
  r1_cordio_gatts_database_bind(pvPortMalloc, vPortFree,
                                 r1_cordio_gatts_write_event);
  r1_cordio_gatts_api_bind(r1_cordio_conn_id_from_nordic,
                           sd_ble_uuid_encode,
                           r1_cordio_gatts_tx_event);
  r1_cordio_adv_set_hooks(r1_cordio_event_adv_terminated,
                          r1_cordio_hci_handle_from_nordic);
  r1_cordio_gap_service_set_ccc_sink(r1_cordio_gatts_ccc_changed);
  r1_cordio_gap_service_init();
  AttsIndInit();
  AttcInit();
  AttRegister(r1_cordio_att_callback);

  SmpHandlerInit(WsfOsSetNextHandler(SmpHandler));
  SmprInit();
  SmprScInit();

  DmRegister(r1_cordio_reset_callback);
  DmConnRegister(DM_CLIENT_ID_APP, r1_cordio_connection_callback);
  DmDevReset();
  r1HostInitialized = true;
}
#endif
