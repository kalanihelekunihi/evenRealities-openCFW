/* Cordio app framework app_slave.c variants, stock
 * D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-profiles\sources\apps\app\app_slave.c,
 * native 0x4B36FC..0x4B371F, 0x4B3746..0x4B374B and 0x4B4720..0x4B4727.
 *
 * The connection-open handlers differ from public r20.05c af/app_slave.c:
 *  - appSlaveConnOpen ends with appConnReadRemoteFeatTimerStart (0x4BB25C) as
 *    in AmbiqSuite R3.2.0, not DmReadRemoteFeatures;
 *  - appSlaveProcConnOpen only stores the connection id. The public and
 *    AmbiqSuite R3.2.0 bodies also start the connection-update timer when
 *    pAppUpdateCfg->idlePeriod != 0; the stock 6-byte body has no such path. */
#include <stdint.h>

extern uint8_t audio_ble_subsystem_link_state_200719c8[]; /* appSlaveCb, RAM 0x200719C8 */
extern void app_conn_read_remote_feat_timer_start_4bb25c(uint8_t connection);
extern void audio_ble_pair_storage_refresh(void); /* AppDbReloadResolvingList 0x47B4D4 */

typedef void (*g2_app_adv_restart_cback_t)(void *event);
#define G2_APP_SLAVE_ADV_RESTART_CBACK 0x7Cu /* appSlaveCb.advRestartCback */
#define G2_APP_CONN_CB_CONN_ID 0x04u         /* appConnCb_t.connId */

void appSlaveProcConnOpen_4b3746(void *event, uint8_t *conn_cb)
{
    /* pCb->connId = (dmConnId_t) pMsg->hdr.param; */
    conn_cb[G2_APP_CONN_CB_CONN_ID] = (uint8_t)*(const uint16_t *)event;
}

void appSlaveConnOpen_4b36fc(void *event, uint8_t *conn_cb)
{
    g2_app_adv_restart_cback_t restart;

    appSlaveProcConnOpen_4b3746(event, conn_cb);
    restart = *(g2_app_adv_restart_cback_t *)(void *)
        (audio_ble_subsystem_link_state_200719c8 + G2_APP_SLAVE_ADV_RESTART_CBACK);
    if (restart != 0)
        restart(event);
    app_conn_read_remote_feat_timer_start_4bb25c((uint8_t)*(const uint16_t *)event);
}

/* Product addition at the end of app_slave.c (after AppSlaveClearAllBondingInfo
 * 0x4B46CE); its only caller is 0x47C9E0. Not in public or AmbiqSuite R3.2.0. */
void app_slave_reload_resolving_list_4b4720(void)
{
    audio_ble_pair_storage_refresh();
}
