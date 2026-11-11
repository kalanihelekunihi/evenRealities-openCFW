/* SPDX-License-Identifier: MIT
 * Stock 0x302a1c: a 4-byte `b 0x30299c` veneer.  The ini_record_335820
 * table holds this address in the word after AOAD_Init (0x30299c), so
 * calling it runs AOAD_Init with the caller's registers untouched. */
extern void opencfw_em9305_stock_30299c(void);
void opencfw_em9305_AOAD_Init_veneer_302a1c(void)
{
  opencfw_em9305_stock_30299c();
}
