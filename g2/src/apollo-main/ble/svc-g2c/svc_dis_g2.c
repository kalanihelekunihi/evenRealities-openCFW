// SPDX-License-Identifier: Apache-2.0
/*
 * Cordio Device Information service (AmbiqSuite R3.2.0 svc_dis.c) with the G2
 * vendor SvcDisAddGroup.
 *
 * Stock SvcDisAddGroup 0x53618C (headless-decomp 12.1.4, g2c campaign):
 *   src = *(char **)(audio_ble_adv_config_state + 4) + 1;   (RAM 0x20003838)
 *   memcpy((void *)0x20003AC4, src, strlen(src)); AttsAddGroup(&svcDisGroup 0x20003B10).
 * The destination 0x20003AC4 is disValSn (serial number). Stock evidence (wave20):
 * the DIS attribute record at ROM 0x6d277c is {pUuid 0x78f654, pValue 0x20003ac4,
 * pLen 0x2000452c, ...}, and the UUID bytes at 0x78f654 are 25 2a
 * (0x2A25 = Serial Number String).
 */
/* Stock has no AttsRemoveGroup (excluded from the pinned atts_main.c, see
 * sources.json) and never calls Svc*RemoveGroup, so the upstream remove
 * functions are routed to a local no-op instead of the absent ATT API. */
#include <stdint.h>
static void g2cAttsRemoveGroupAbsent(uint16_t startHandle) { (void)startHandle; }
#define AttsRemoveGroup g2cAttsRemoveGroupAbsent
#define SvcDisAddGroup svcDisAddGroupUpstream
#include "svc_dis.c"
#undef SvcDisAddGroup
#include <stddef.h>

/* Evidence (sim stk12, hook on stock AttsAddGroup 0x5353AE plus a dump of the
 * stock image): stock svcDisGroup 0x20003B10 = {pAttr 0x6d271c, start 48,
 * end 58}, 11 attributes: svc 180A; then 2A29, 2A24, 2A25, 2A26, 2A27, whose
 * characteristic declarations at 0x78e95c..0x78e97c are
 * 02 3200 292a / 02 3400 242a / 02 3600 252a / 02 3800 262a / 02 3a00 272a.
 * There is no System ID, SW rev, 11073 cert or PnP ID. */
static const uint8_t g2DisValMfrCh[] = {ATT_PROP_READ, UINT16_TO_BYTES(0x32), UINT16_TO_BYTES(ATT_UUID_MANUFACTURER_NAME)};
static const uint8_t g2DisValMnCh[]  = {ATT_PROP_READ, UINT16_TO_BYTES(0x34), UINT16_TO_BYTES(ATT_UUID_MODEL_NUMBER)};
static const uint8_t g2DisValSnCh[]  = {ATT_PROP_READ, UINT16_TO_BYTES(0x36), UINT16_TO_BYTES(ATT_UUID_SERIAL_NUMBER)};
static const uint8_t g2DisValFwrCh[] = {ATT_PROP_READ, UINT16_TO_BYTES(0x38), UINT16_TO_BYTES(ATT_UUID_FIRMWARE_REV)};
static const uint8_t g2DisValHwrCh[] = {ATT_PROP_READ, UINT16_TO_BYTES(0x3a), UINT16_TO_BYTES(ATT_UUID_HARDWARE_REV)};
static const uint16_t g2DisLenCh = 5;
#define G2_DIS_CH(v) { attChUuid, (uint8_t *)(v), (uint16_t *)&g2DisLenCh, 5, 0, ATTS_PERMIT_READ }
static const attsAttr_t g2DisList[] =
{
  { attPrimSvcUuid, (uint8_t *)disValSvc, (uint16_t *)&disLenSvc, sizeof(disValSvc), 0, ATTS_PERMIT_READ },
  G2_DIS_CH(g2DisValMfrCh),
  { disUuMfr, (uint8_t *)disValMfr, (uint16_t *)&disLenMfr, sizeof(disValMfr), ATTS_SET_VARIABLE_LEN, DIS_SEC_PERMIT_READ },
  G2_DIS_CH(g2DisValMnCh), 
  { disUuMn, (uint8_t *)disValMn, (uint16_t *)&disLenMn, sizeof(disValMn), ATTS_SET_VARIABLE_LEN, DIS_SEC_PERMIT_READ },
  G2_DIS_CH(g2DisValSnCh), 
  { disUuSn, (uint8_t *)disValSn, (uint16_t *)&disLenSn, sizeof(disValSn), ATTS_SET_VARIABLE_LEN, DIS_SEC_PERMIT_READ },
  G2_DIS_CH(g2DisValFwrCh),
  { disUuFwr, (uint8_t *)disValFwr, (uint16_t *)&disLenFwr, sizeof(disValFwr), ATTS_SET_VARIABLE_LEN, DIS_SEC_PERMIT_READ },
  G2_DIS_CH(g2DisValHwrCh),
  { disUuHwr, (uint8_t *)disValHwr, (uint16_t *)&disLenHwr, sizeof(disValHwr), ATTS_SET_VARIABLE_LEN, DIS_SEC_PERMIT_READ },
};

extern uint8_t audio_ble_adv_config_state[];
extern size_t strlen(const char *);
extern void *memcpy(void *, const void *, size_t);

void SvcDisAddGroup(void)
{
  const char *src = *(char *const *)(void *)(audio_ble_adv_config_state + 4) + 1;
  memcpy(disValSn, src, strlen(src));
  svcDisGroup.pAttr = (attsAttr_t *)g2DisList;
  svcDisGroup.endHandle = (uint16_t)(DIS_START_HDL + 10u);
  AttsAddGroup(&svcDisGroup);
}
