/* R1 controller and integrated ExactLE host bootstrap. The caller must have
 * initialized nrf_drv_clock and enabled interrupts before entering here.
 * WSF dispatch and the Nordic sd_* API adapter are separate owners. */
#if defined(R1_CORDIO_RTC0)
#include <stdbool.h>
#include <stdint.h>

#include "cordio_controller_bootstrap.h"

#include "cfg_mac_ble.h"
#include "hci_defs.h"
#include "hci_handler.h"
#include "ll_api.h"
#include "ll_init_api.h"
#include "pal_bb.h"
#include "pal_cfg.h"
#include "pal_sys.h"
#include "wsf_buf.h"
#include "wsf_heap.h"
#include "wsf_os.h"
#include "wsf_timer.h"

_Static_assert(BT_VER == LL_VER_BT_CORE_SPEC_5_0 && LL_MAX_PER_SCAN == 1,
               "R1 Cordio compile-time feature and scanner profile");
#if defined(INIT_CENTRAL) || defined(INIT_OBSERVER)
#error "R1 Cordio bootstrap is configured for peripheral roles only"
#endif

static BbRtCfg_t r1BbCfg;
static LlRtCfg_t r1LlCfg;
static bool r1ControllerAttempted;
static bool r1ControllerInitialized;

bool r1_cordio_controller_bootstrap(void)
{
  if (r1ControllerInitialized)
  {
    return true;
  }
  if (r1ControllerAttempted)
  {
    return false;
  }
  r1ControllerAttempted = true;

  PalSysInit();
  PalBbLoadCfg((PalBbCfg_t *)&r1BbCfg);
  LlGetDefaultRunTimeCfg(&r1LlCfg);
  PalCfgLoadData(PAL_CFG_ID_LL_PARAM, &r1LlCfg.maxAdvSets,
                 sizeof(r1LlCfg) - 9u);
  PalCfgLoadData(PAL_CFG_ID_BLE_PHY, &r1LlCfg.phy2mSup, 4u);
  r1LlCfg.btVer = LL_VER_BT_CORE_SPEC_5_0;

  const uint16_t reportBufSize = 12u + 2u + 255u;
  const uint16_t dataBufSize = 12u + HCI_ISO_DL_MAX_LEN +
                               r1LlCfg.maxAclLen + 4u + BB_DATA_PDU_TAILROOM;
  if (r1LlCfg.maxAclLen != r1LlCfg.maxIsoSduLen ||
      reportBufSize >= dataBufSize)
  {
    return false;
  }

  wsfBufPoolDesc_t pools[] = {
    {16u, 8u},
    {32u, 4u},
    {128u, r1LlCfg.maxAdvReports},
    {reportBufSize, r1LlCfg.maxAdvReports},
    {dataBufSize, r1LlCfg.numTxBufs + r1LlCfg.numRxBufs +
                  r1LlCfg.numIsoTxBuf + r1LlCfg.numIsoRxBuf}
  };
  const uint8_t poolCount = sizeof(pools) / sizeof(pools[0]);
  const uint32_t poolBytes = WsfBufCalcSize(poolCount, pools);
  if (poolBytes == 0u || poolBytes > WsfHeapCountAvailable())
  {
    return false;
  }
  const uint32_t initializedPoolBytes = WsfBufInit(poolCount, pools);
  if (initializedPoolBytes != poolBytes)
  {
    return false;
  }
  WsfHeapAlloc(initializedPoolBytes);
  WsfOsInit();
  WsfTimerInit();

  LlInitRtCfg_t controllerCfg = {
    .pBbRtCfg = &r1BbCfg,
    .wlSizeCfg = 4u,
    .rlSizeCfg = 4u,
    .plSizeCfg = 4u,
    .pLlRtCfg = &r1LlCfg,
    .pFreeMem = WsfHeapGetFreeStartAddress(),
    .freeMemAvail = WsfHeapCountAvailable()
  };
  const uint32_t controllerBytes = LlInitControllerInit(&controllerCfg);
  if (controllerBytes == 0u || controllerBytes > WsfHeapCountAvailable())
  {
    return false;
  }
  WsfHeapAlloc(controllerBytes);
  uint8_t address[6];
  PalCfgLoadData(PAL_CFG_ID_BD_ADDR, address, sizeof(address));
  LlSetBdAddr(address);
  /* LlMathSetSeed consumes one word. Build it from the first four BLE
   * address bytes without relying on the address array's alignment. */
  uint32_t seed = (uint32_t)address[0] | ((uint32_t)address[1] << 8) |
                  ((uint32_t)address[2] << 16) | ((uint32_t)address[3] << 24);
  LlMathSetSeed(&seed);

  /* HciHandlerInit registers the integrated host's LL/ACL callbacks after
   * controller initialization registers LHCI callbacks. */
  HciHandlerInit(WsfOsSetNextHandler(HciHandler));
  r1ControllerInitialized = true;
  return true;
}
#endif
