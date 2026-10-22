/* Ring protocol service helpers, stock D:\01_workspace\s200_ap510b_iar_git\platform\protocols\ring_service\ring_service.c.
 * Native 0x472596..0x47262f and 0x4728a0..0x4728b1 (literal pool 0x472bb8..0x472c27).
 * Neighbours owned elsewhere: 0x472426 (ring touch enable message) in
 * ble/ble-master/display_ble_master_touch_followup.c and 0x47243a (RING_SendGlassesStatusEvt)
 * in app/status/display_status.c.
 *
 * Both rows are called from the BLE central message handler _masterProcMsg (0x4a06d4):
 * the PHY request on ring connection, the wear-state reset on ring disconnect. */
#include <stdint.h>

/* Cordio HCI PHY bits: transmit on LE Coded, receive on LE 1M, prefer S=8 coding. */
#define RING_PHY_ALL_PHYS 0u
#define RING_PHY_TX_CODED 4u
#define RING_PHY_RX_1M 1u
#define RING_PHY_OPTIONS_S8 2u

extern volatile uint8_t audio_uart_ring_worn;       /* RAM 0x2007500c */
extern volatile uint32_t audio_uart_ring_wear_tick; /* RAM 0x20074904 */

extern void DmSetPhy(uint8_t conn_id, uint8_t all_phys, uint8_t tx_phys, uint8_t rx_phys, uint16_t phy_options); /* 0x4c5810 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "ring.proto"; /* ROM 0x78bdb0 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\ring_service\\ring_service.c"; /* ROM 0x6e99a0 */
static const char set_phy_fn[] = "RING_SetPhyProcess"; /* ROM 0x782d80 */
static const char set_phy_msg[] = "RING_SetPhyProcess connId: %d, txPhys: %d, rxPhys: %d, phyOptions: %d"; /* ROM 0x6fc8e4 */
static const char set_phy_short[] =
    "[ring.proto]RING_SetPhyProcess connId: %d, txPhys: %d, rxPhys: %d, phyOptions: %d"; /* ROM 0x6e99f4 */

uint32_t ring_set_phy_process_472596(uint8_t conn_id)
{
    uint8_t tx_phys = RING_PHY_TX_CODED;
    uint8_t rx_phys = RING_PHY_RX_1M;
    uint16_t phy_options = RING_PHY_OPTIONS_S8;

    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, set_phy_fn, 0x1b8u, set_phy_msg,
                           (uint32_t)conn_id, (uint32_t)tx_phys, (uint32_t)rx_phys, (uint32_t)phy_options);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0d000000u, set_phy_short, set_phy_short,
                                  (uint32_t)conn_id, (uint32_t)tx_phys, (uint32_t)rx_phys, (uint32_t)phy_options);
    DmSetPhy(conn_id, RING_PHY_ALL_PHYS, tx_phys, rx_phys, phy_options);
    return 0u;
}

void ring_wear_state_reset_4728a0(void)
{
    audio_uart_ring_worn = 0u;
    audio_uart_ring_wear_tick = 0u;
}
