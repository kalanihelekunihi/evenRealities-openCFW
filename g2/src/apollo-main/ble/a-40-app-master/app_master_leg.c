/* Cordio legacy-scan master wrappers, stock
 * D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-profiles\sources\apps\app\app_master_leg.c.
 * Native 0x503298..0x50345d; literal pool 0x503460..0x503497.
 *
 * Same control flow as upstream Cordio app_master_leg.c (third-party/upstream/cordio
 * ble-profiles/sources/af/app_master_leg.c), with the product logger in place of
 * APP_TRACE: appMasterScanMode logs the mode it accepts, AppConnOpen logs both
 * outcomes. appMasterCb lives at RAM 0x20071670 (scanMode +0x9d, inProgress +0x9c). */
#include <stdint.h>

#define APP_SCAN_MODE_LEG 0u
#define APP_SCAN_MODE_NONE 0xffu
#define HCI_SCAN_PHY_LE_1M_BIT 1u
#define HCI_INIT_PHY_LE_1M_BIT 1u
#define DM_CONN_ID_NONE 0u

#define APP_MASTER_IN_PROGRESS 0x9cu
#define APP_MASTER_SCAN_MODE 0x9du

/* appMasterCfg_t: scanInterval at +0, scanWindow at +2. */
typedef struct {
    uint16_t scan_interval;
    uint16_t scan_window;
} g2_app_master_cfg_t;

extern volatile uint8_t audio_ble_subsystem_state_20071670[]; /* appMasterCb, 0x9e bytes */
extern const g2_app_master_cfg_t *g2_app_master_cfg;         /* RAM 0x20074354 pAppMasterCfg */

extern void DmScanSetInterval_55bb68(uint8_t scan_phys, const uint16_t *scan_interval,
                                     const uint16_t *scan_window);
extern void DmScanStart_55baae(uint8_t scan_phys, uint8_t mode, const uint8_t *scan_type,
                               uint8_t filter_dup, uint16_t duration, uint16_t period);
extern void DmScanStop_55bb1e(void);
extern uint8_t appConnOpen_503d1e(uint8_t init_phys, uint8_t addr_type, uint8_t *addr,
                                  uint32_t db_hdl);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);

static const char module_tag[] = "master.leg"; /* ROM 0x78a2c8 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\app_master_leg.c"; /* ROM 0x6d85f4 */
static const char scan_mode_fn[] = "appMasterScanMode"; /* ROM 0x77e0f0 */
static const char scan_mode_text[] = "appMasterCb.scanMode = %d"; /* ROM 0x769794 */
static const char scan_mode_short[] = "[master.leg]appMasterCb.scanMode = %d"; /* ROM 0x747a44 */
static const char invalid_mode[] = "Invalid DM scanning mode; mode configured as extended"; /* ROM 0x71c2d8 */
static const char invalid_mode_short[] =
    "[master.leg]Invalid DM scanning mode; mode configured as extended"; /* ROM 0x7007cc */
static const char conn_open_fn[] = "AppConnOpen"; /* ROM 0x78a2d4 */
static const char conn_open_text[] = "AppConnOpen"; /* ROM 0x78a2e0 */
static const char conn_open_short[] = "[master.leg]AppConnOpen"; /* ROM 0x7754c4 */
static const char wrong_mode[] = "AppConnOpen wrong connect mode"; /* ROM 0x75e070 */
static const char wrong_mode_short[] = "[master.leg]AppConnOpen wrong connect mode"; /* ROM 0x73c324 */

#define LOG_EXT_ON() ((audio_log_flags() & 2u) != 0u)
#define LOG_CMP_ON() ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)

static void log_scan_mode(uint32_t line)
{
    if (LOG_EXT_ON())
        audio_log_extended(4u, module_tag, source_file, scan_mode_fn, line, scan_mode_text,
                           audio_ble_subsystem_state_20071670[APP_MASTER_SCAN_MODE]);
    if (LOG_CMP_ON())
        (void)compress_log_output(0x10400000u, scan_mode_short, scan_mode_short,
                                  audio_ble_subsystem_state_20071670[APP_MASTER_SCAN_MODE]);
}

uint8_t appMasterScanMode(void)
{
    if (audio_ble_subsystem_state_20071670[APP_MASTER_SCAN_MODE] == APP_SCAN_MODE_NONE) {
        audio_ble_subsystem_state_20071670[APP_MASTER_SCAN_MODE] = APP_SCAN_MODE_LEG;
        log_scan_mode(0x32u);
        return 1u;
    }
    if (audio_ble_subsystem_state_20071670[APP_MASTER_SCAN_MODE] == APP_SCAN_MODE_LEG) {
        log_scan_mode(0x38u);
        return 1u;
    }
    if (LOG_EXT_ON())
        audio_log_extended(4u, module_tag, source_file, scan_mode_fn, 0x3cu, invalid_mode);
    if (LOG_CMP_ON())
        (void)compress_log_output(0x10000000u, invalid_mode_short, invalid_mode_short);
    return 0u;
}

void AppScanStart(uint8_t mode, uint8_t scan_type, uint16_t duration)
{
    if (appMasterScanMode() == 0u)
        return;
    DmScanSetInterval_55bb68(HCI_SCAN_PHY_LE_1M_BIT, &g2_app_master_cfg->scan_interval,
                             &g2_app_master_cfg->scan_window);
    DmScanStart_55baae(HCI_SCAN_PHY_LE_1M_BIT, mode, &scan_type, 1u, duration, 0u);
}

void AppScanStop(void)
{
    if (appMasterScanMode() == 0u)
        return;
    audio_ble_subsystem_state_20071670[APP_MASTER_IN_PROGRESS] = 0u; /* stop address resolution */
    DmScanStop_55bb1e();
}

uint8_t AppConnOpen(uint8_t addr_type, uint8_t *addr, uint32_t db_hdl)
{
    if (appMasterScanMode() != 0u) {
        if (LOG_EXT_ON())
            audio_log_extended(4u, module_tag, source_file, conn_open_fn, 0x79u, conn_open_text);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x10000000u, conn_open_short, conn_open_short);
        return appConnOpen_503d1e(HCI_INIT_PHY_LE_1M_BIT, addr_type, addr, db_hdl);
    }
    if (LOG_EXT_ON())
        audio_log_extended(4u, module_tag, source_file, conn_open_fn, 0x7cu, wrong_mode);
    if (LOG_CMP_ON())
        (void)compress_log_output(0x10000000u, wrong_mode_short, wrong_mode_short);
    return DM_CONN_ID_NONE;
}
