/* R1 legacy-bonding adapter between Nordic GAP and Cordio SMP. */
#if defined(R1_CORDIO_RTC0)
#include <stddef.h>
#include <string.h>

#include "ble.h"
#include "nrf_error.h"
#include "dm_api.h"
#include "smp_defs.h"
#include "cordio_ble_event_bridge.h"
#include "r1_security_cordio.h"

enum { R1_SECURITY_LINKS = 3, R1_SECURITY_EVENT_BYTES = BLE_EVT_LEN_MAX(247) };
typedef struct {
    ble_gap_sec_keys_t own;
    ble_gap_sec_keys_t peer;
    uint8_t peer_initiator_dist;
    uint8_t peer_responder_dist;
    uint8_t own_keys_received;
    uint8_t peer_keys_received;
    uint8_t pair_pending;
    uint8_t ltk_pending;
    uint8_t requested;
    uint8_t key_length;
    uint8_t auth;
} r1_security_link_t;

static r1_security_link_t links[R1_SECURITY_LINKS];
/* The WSF task is the only DM event producer. Keep large Nordic event
 * records off its 2 KiB stack. publish() copies before returning. */
static uint32_t event_words[R1_SECURITY_EVENT_BYTES / sizeof(uint32_t)];

static ble_evt_t *new_event(uint8_t conn_id, uint16_t event_id)
{
    ble_evt_t *event = (ble_evt_t *)event_words;
    memset(event, 0, sizeof(event_words));
    event->header.evt_id = event_id;
    event->header.evt_len = (uint16_t)sizeof(ble_evt_t);
    event->evt.gap_evt.conn_handle = (uint16_t)(conn_id - 1u);
    return event;
}

static bool send_event(ble_evt_t *event)
{
    return r1_cordio_ble_event_publish(event, event->header.evt_len);
}

static uint8_t auth_bits(const ble_gap_sec_params_t *params)
{
    return (uint8_t)((params->bond ? DM_AUTH_BOND_FLAG : 0u) |
                     (params->mitm ? DM_AUTH_MITM_FLAG : 0u) |
                     (params->lesc ? DM_AUTH_SC_FLAG : 0u) |
                     (params->keypress ? DM_AUTH_KP_FLAG : 0u));
}

static uint8_t distribution(ble_gap_sec_kdist_t dist)
{
    return (uint8_t)((dist.enc ? DM_KEY_DIST_LTK : 0u) |
                     (dist.id ? DM_KEY_DIST_IRK : 0u) |
                     (dist.sign ? DM_KEY_DIST_CSRK : 0u));
}

static void nordic_distribution(ble_gap_sec_kdist_t *dist, uint8_t flags)
{
    dist->enc = (flags & DM_KEY_DIST_LTK) != 0u;
    dist->id = (flags & DM_KEY_DIST_IRK) != 0u;
    dist->sign = (flags & DM_KEY_DIST_CSRK) != 0u;
}

void r1_cordio_security_reset(uint8_t conn_id)
{
    if (conn_id < 1u || conn_id > R1_SECURITY_LINKS) return;
    memset(&links[conn_id - 1u], 0, sizeof(links[0]));
}

uint32_t sd_ble_gap_authenticate(uint16_t conn_handle,
                                  ble_gap_sec_params_t const *params)
{
    uint8_t conn_id = r1_cordio_conn_id_from_nordic(conn_handle);
    if (conn_id == 0u) return BLE_ERROR_INVALID_CONN_HANDLE;
    if (params == 0) return NRF_ERROR_INVALID_ADDR;
    if (params->kdist_own.sign || params->kdist_own.link ||
        params->kdist_peer.sign || params->kdist_peer.link)
        return NRF_ERROR_NOT_SUPPORTED;
    r1_security_link_t *link = &links[conn_id - 1u];
    if (link->requested || link->pair_pending)
        return NRF_ERROR_INVALID_STATE;
    link->requested = 1u;
    link->auth = auth_bits(params);
    DmSecSlaveReq(conn_id, link->auth);
    return NRF_SUCCESS;
}

uint32_t sd_ble_gap_sec_params_reply(
    uint16_t conn_handle, uint8_t status,
    ble_gap_sec_params_t const *params,
    ble_gap_sec_keyset_t const *keys)
{
    uint8_t conn_id = r1_cordio_conn_id_from_nordic(conn_handle);
    if (conn_id == 0u) return BLE_ERROR_INVALID_CONN_HANDLE;
    r1_security_link_t *link = &links[conn_id - 1u];
    if (!link->pair_pending) return NRF_ERROR_INVALID_STATE;
    if (status != BLE_GAP_SEC_STATUS_SUCCESS) {
        if (status < BLE_GAP_SEC_STATUS_PASSKEY_ENTRY_FAILED ||
            status > BLE_GAP_SEC_STATUS_X_TRANS_KEY_DISALLOWED)
            return NRF_ERROR_INVALID_PARAM;
        link->pair_pending = 0u;
        DmSecCancelReq(conn_id, (uint8_t)(status - 0x80u));
        return NRF_SUCCESS;
    }
    if (params == 0 || keys == 0) return NRF_ERROR_INVALID_ADDR;
    if (params->lesc || params->mitm || params->oob ||
        params->io_caps != BLE_GAP_IO_CAPS_NONE ||
        params->min_key_size < 7u || params->max_key_size > 16u ||
        params->max_key_size < params->min_key_size ||
        params->kdist_own.sign || params->kdist_own.link ||
        params->kdist_peer.sign || params->kdist_peer.link)
        return NRF_ERROR_NOT_SUPPORTED;
    uint8_t initiator = distribution(params->kdist_peer) &
                        link->peer_initiator_dist;
    uint8_t responder = distribution(params->kdist_own) &
                        link->peer_responder_dist;
    /* The current source candidate has no persisted local IRK. Never ask
     * Cordio to dereference an unset IRK or distribute a transient one. */
    responder &= (uint8_t)~DM_KEY_DIST_IRK;
    link->own = keys->keys_own;
    link->peer = keys->keys_peer;
    link->auth = auth_bits(params);
    link->pair_pending = 0u;
    DmSecPairRsp(conn_id, 0u, link->auth, initiator, responder);
    return NRF_SUCCESS;
}

uint32_t sd_ble_gap_sec_info_reply(
    uint16_t conn_handle, ble_gap_enc_info_t const *enc_info,
    ble_gap_irk_t const *id_info, ble_gap_sign_info_t const *sign_info)
{
    uint8_t conn_id = r1_cordio_conn_id_from_nordic(conn_handle);
    if (conn_id == 0u) return BLE_ERROR_INVALID_CONN_HANDLE;
    r1_security_link_t *link = &links[conn_id - 1u];
    if (!link->ltk_pending) return NRF_ERROR_INVALID_STATE;
    if (id_info != 0 || sign_info != 0) return NRF_ERROR_NOT_SUPPORTED;
    if (enc_info != 0 &&
        (enc_info->ltk_len < 7u || enc_info->ltk_len > 16u))
        return NRF_ERROR_INVALID_PARAM;
    link->ltk_pending = 0u;
    if (enc_info != 0) link->key_length = enc_info->ltk_len;
    DmSecLtkRsp(conn_id, enc_info != 0,
                enc_info == 0 ? DM_SEC_LEVEL_NONE :
                (enc_info->lesc ? DM_SEC_LEVEL_ENC_LESC :
                 enc_info->auth ? DM_SEC_LEVEL_ENC_AUTH : DM_SEC_LEVEL_ENC),
                enc_info == 0 ? 0 : (uint8_t *)enc_info->ltk);
    return NRF_SUCCESS;
}

static bool pair_requested(const dmEvt_t *dm)
{
    uint8_t conn_id = dm->hdr.param;
    r1_security_link_t *link = &links[conn_id - 1u];
    link->pair_pending = 1u;
    link->peer_initiator_dist = dm->pairInd.iKeyDist;
    link->peer_responder_dist = dm->pairInd.rKeyDist;
    ble_evt_t *event = new_event(conn_id, BLE_GAP_EVT_SEC_PARAMS_REQUEST);
    ble_gap_sec_params_t *params =
        &event->evt.gap_evt.params.sec_params_request.peer_params;
    params->bond = (dm->pairInd.auth & DM_AUTH_BOND_FLAG) != 0u;
    params->mitm = (dm->pairInd.auth & DM_AUTH_MITM_FLAG) != 0u;
    params->lesc = (dm->pairInd.auth & DM_AUTH_SC_FLAG) != 0u;
    params->keypress = (dm->pairInd.auth & DM_AUTH_KP_FLAG) != 0u;
    params->oob = dm->pairInd.oob != 0u;
    params->io_caps = BLE_GAP_IO_CAPS_NONE;
    params->min_key_size = 7u;
    params->max_key_size = 16u;
    nordic_distribution(&params->kdist_own, dm->pairInd.iKeyDist);
    nordic_distribution(&params->kdist_peer, dm->pairInd.rKeyDist);
    return send_event(event);
}

static bool ltk_requested(const dmEvt_t *dm)
{
    uint8_t conn_id = dm->hdr.param;
    links[conn_id - 1u].ltk_pending = 1u;
    ble_evt_t *event = new_event(conn_id, BLE_GAP_EVT_SEC_INFO_REQUEST);
    ble_gap_evt_sec_info_request_t *request =
        &event->evt.gap_evt.params.sec_info_request;
    request->master_id.ediv = dm->ltkReqInd.encDiversifier;
    memcpy(request->master_id.rand, dm->ltkReqInd.randNum,
           sizeof(request->master_id.rand));
    request->enc_info = 1u;
    const uint8_t *address = DmConnPeerAddr(conn_id);
    if (address != 0) memcpy(request->peer_addr.addr, address, 6u);
    request->peer_addr.addr_type = DmConnPeerAddrType(conn_id) == DM_ADDR_PUBLIC ?
                                   BLE_GAP_ADDR_TYPE_PUBLIC :
                                   BLE_GAP_ADDR_TYPE_RANDOM_STATIC;
    return send_event(event);
}

static void copy_ltk(ble_gap_enc_key_t *destination,
                     const dmSecKeyIndEvt_t *key)
{
    if (destination == 0) return;
    memcpy(destination->enc_info.ltk, key->keyData.ltk.key, 16u);
    destination->enc_info.ltk_len = key->encKeyLen;
    destination->enc_info.auth = key->secLevel >= DM_SEC_LEVEL_ENC_AUTH;
    destination->enc_info.lesc = key->secLevel >= DM_SEC_LEVEL_ENC_LESC;
    destination->master_id.ediv = key->keyData.ltk.ediv;
    memcpy(destination->master_id.rand, key->keyData.ltk.rand, 8u);
}

static void key_received(const dmEvt_t *dm)
{
    r1_security_link_t *link = &links[dm->hdr.param - 1u];
    if (dm->keyInd.type == DM_KEY_LOCAL_LTK) {
        copy_ltk(link->own.p_enc_key, &dm->keyInd);
        link->own_keys_received |= DM_KEY_DIST_LTK;
        link->key_length = dm->keyInd.encKeyLen;
    } else if (dm->keyInd.type == DM_KEY_PEER_LTK) {
        copy_ltk(link->peer.p_enc_key, &dm->keyInd);
        link->peer_keys_received |= DM_KEY_DIST_LTK;
        link->key_length = dm->keyInd.encKeyLen;
    } else if (dm->keyInd.type == DM_KEY_IRK) {
        if (link->peer.p_id_key != 0) {
            memcpy(link->peer.p_id_key->id_info.irk,
                   dm->keyInd.keyData.irk.key, 16u);
            memcpy(link->peer.p_id_key->id_addr_info.addr,
                   dm->keyInd.keyData.irk.bdAddr, 6u);
            link->peer.p_id_key->id_addr_info.addr_type =
                dm->keyInd.keyData.irk.addrType == DM_ADDR_PUBLIC ?
                BLE_GAP_ADDR_TYPE_PUBLIC : BLE_GAP_ADDR_TYPE_RANDOM_STATIC;
        }
        link->peer_keys_received |= DM_KEY_DIST_IRK;
    }
}

static bool pairing_done(const dmEvt_t *dm, uint8_t status)
{
    uint8_t conn_id = dm->hdr.param;
    r1_security_link_t *link = &links[conn_id - 1u];
    ble_evt_t *event = new_event(conn_id, BLE_GAP_EVT_AUTH_STATUS);
    ble_gap_evt_auth_status_t *auth = &event->evt.gap_evt.params.auth_status;
    auth->auth_status = status;
    auth->error_src = BLE_GAP_SEC_STATUS_SOURCE_REMOTE;
    auth->bonded = status == 0u && (link->auth & DM_AUTH_BOND_FLAG) != 0u;
    auth->lesc = status == 0u && (link->auth & DM_AUTH_SC_FLAG) != 0u;
    if (status == 0u) auth->sm1_levels.lv2 = 1u;
    nordic_distribution(&auth->kdist_own, link->own_keys_received);
    nordic_distribution(&auth->kdist_peer, link->peer_keys_received);
    link->requested = 0u;
    link->pair_pending = 0u;
    return send_event(event);
}

static bool encryption_changed(const dmEvt_t *dm, bool encrypted)
{
    uint8_t conn_id = dm->hdr.param;
    r1_security_link_t *link = &links[conn_id - 1u];
    ble_evt_t *event = new_event(conn_id, BLE_GAP_EVT_CONN_SEC_UPDATE);
    ble_gap_conn_sec_t *security =
        &event->evt.gap_evt.params.conn_sec_update.conn_sec;
    security->sec_mode.sm = 1u;
    uint8_t level = encrypted ? DmConnSecLevel(conn_id) : DM_SEC_LEVEL_NONE;
    security->sec_mode.lv = level == DM_SEC_LEVEL_NONE ? 1u :
                            level == DM_SEC_LEVEL_ENC ? 2u :
                            level == DM_SEC_LEVEL_ENC_AUTH ? 3u : 4u;
    security->encr_key_size = encrypted ?
        (link->key_length != 0u ? link->key_length : 16u) : 0u;
    return send_event(event);
}

bool r1_cordio_security_dm_event(const void *message)
{
    const dmEvt_t *dm = (const dmEvt_t *)message;
    if (dm == 0 || dm->hdr.param < 1u ||
        dm->hdr.param > R1_SECURITY_LINKS) return false;
    switch (dm->hdr.event) {
    case DM_SEC_PAIR_IND: return pair_requested(dm);
    case DM_SEC_LTK_REQ_IND: return ltk_requested(dm);
    case DM_SEC_KEY_IND: key_received(dm); return true;
    case DM_SEC_PAIR_CMPL_IND: return pairing_done(dm, BLE_GAP_SEC_STATUS_SUCCESS);
    case DM_SEC_PAIR_FAIL_IND:
        return pairing_done(dm, dm->hdr.status <= 0x0eu ?
            (uint8_t)(0x80u + dm->hdr.status) :
            BLE_GAP_SEC_STATUS_UNSPECIFIED);
    case DM_SEC_ENCRYPT_IND: return encryption_changed(dm, true);
    case DM_SEC_ENCRYPT_FAIL_IND: return encryption_changed(dm, false);
    default: return false;
    }
}
#endif
