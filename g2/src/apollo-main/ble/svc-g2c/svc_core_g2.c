// SPDX-License-Identifier: Apache-2.0
/*
 * Cordio GAP/GATT core service (AmbiqSuite R3.2.0 svc_core.c) with the G2
 * vendor SvcCoreAddGroup.
 *
 * Stock (headless-decomp 12.1.4, g2c campaign):
 *   SvcCoreAddGroup 0x52DBF0: gapLenDn (RAM 0x20004532) = strlen(APP_BleNameGet());
 *     memcpy(gapValDn (0x20003B60), APP_BleNameGet(), gapLenDn);
 *     AttsAddGroup(&svcGapGroup 0x20003B7C); AttsAddGroup(&svcGattGroup 0x20003B90).
 *   SvcCoreGattCbackRegister 0x52DC1C: upstream body.
 * The attribute tables are the upstream defaults compiled under the recovered
 * Cordio configuration; their initial values are not yet byte-checked against
 * the stock .data image (ledger item).
 */
/* Stock has no AttsRemoveGroup (excluded from the pinned atts_main.c, see
 * sources.json) and never calls Svc*RemoveGroup, so the upstream remove
 * functions are routed to a local no-op instead of the absent ATT API. */
#include <stdint.h>
static void g2cAttsRemoveGroupAbsent(uint16_t startHandle) { (void)startHandle; }
#define AttsRemoveGroup g2cAttsRemoveGroupAbsent
#define SvcCoreAddGroup svcCoreAddGroupUpstream
#include "svc_core.c"
#undef SvcCoreAddGroup
#include <stddef.h>

extern char *APP_BleNameGet(void);
extern size_t strlen(const char *);
extern void *memcpy(void *, const void *, size_t);

void SvcCoreAddGroup(void)
{
  gapLenDn = (uint16_t)strlen(APP_BleNameGet());
  memcpy(gapValDn, APP_BleNameGet(), gapLenDn);
  AttsAddGroup(&svcGapGroup);
  /* Evidence (sim stk12, hook on stock AttsAddGroup 0x5353AE): stock
   * svcGattGroup 0x20003B90 = {pAttr 0x6d5ad8, start 16, end 23}; the stock
   * table holds 8 attributes (svc, 2A05 + CCC, 2B29, 2B2A) and no Server
   * Supported Features (2B3A) pair, which upstream appends last.  Trimming
   * the end handle drops exactly that pair, so the DB-hash input fits the
   * 480-byte WSF pool as in stock. */
  svcGattGroup.endHandle = (uint16_t)(GATT_START_HDL + 7u);
  AttsAddGroup(&svcGattGroup);
}
