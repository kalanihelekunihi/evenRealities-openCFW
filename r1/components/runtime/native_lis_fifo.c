#include <stdint.h>
#include <stddef.h>
#include "lis2dw12_reg.h"
/* Only the observed16-byte context prefix is owned. The pinned ST header also
 * has a trailing private pointer; none of these entries reads that field. */
struct r1_lis_context_prefix {uint32_t write,read,delay,handle;};
_Static_assert(sizeof(struct r1_lis_context_prefix)==16 && offsetof(struct r1_lis_context_prefix,read)==4 && offsetof(struct r1_lis_context_prefix,handle)==12,"observed native context prefix");
struct r1_lis_context_prefix r1_lis_context __attribute__((section(".bss.r1.lis.context"),aligned(4)));
extern int32_t r1_lis_fifo_level_body(const stmdev_ctx_t *,uint8_t *,volatile uint8_t *);
/* Strong replacement for the upstream weak read wrapper: native is unguarded
 * and captures handle before callback. The upstream level algorithm is reused. */
__attribute__((naked)) int32_t lis2dw12_read_reg(const stmdev_ctx_t *ctx __attribute__((unused)),uint8_t reg __attribute__((unused)),uint8_t *data __attribute__((unused)),uint16_t length __attribute__((unused)))
{
 __asm__ volatile("push {r4,r5}\nldr r4,[r0,#12]\nldr r5,[r0,#4]\nmov r0,r4\nmov r12,r5\npop {r4,r5}\nbx r12\n");
}
__attribute__((naked)) int32_t lis2dw12_fifo_data_level_get(const stmdev_ctx_t *ctx __attribute__((unused)),uint8_t *value __attribute__((unused)))
{
 __asm__ volatile("push {r3,r4,r5,lr}\nmov r2,sp\nbl r1_lis_fifo_level_body\npop {r3,r4,r5,pc}\n");
}
__attribute__((naked)) int32_t r1_lis2dw12_fifo_burst_read(const stmdev_ctx_t *ctx __attribute__((unused)),uint8_t *destination __attribute__((unused)),uint32_t samples __attribute__((unused)))
{
 __asm__ volatile("add.w r2,r2,r2,lsl #1\nmovw r3,#65535\nand.w r3,r3,r2,lsl #1\npush {r4,lr}\nmov r2,r1\nmovs r1,#40\nbl lis2dw12_read_reg\npop {r4,pc}\n");
}
__attribute__((naked)) int32_t r1_lis2dw12_fifo_read(uint8_t *destination __attribute__((unused)),uint32_t requested __attribute__((unused)))
{
 __asm__ volatile("push {r3,r4,r5,lr}\nmov r5,r0\nmovs r0,#0\nmov r4,r1\nstrb r0,[sp]\nmov r1,sp\nldr r0,=r1_lis_context\nbl lis2dw12_fifo_data_level_get\nldrb r1,[sp]\ncbz r1,2f\ncmp r1,r4\nbls 1f\nstrb r4,[sp]\n1: ldrb r2,[sp]\nmov r1,r5\nldr r0,=r1_lis_context\nbl r1_lis2dw12_fifo_burst_read\n2: ldrb r0,[sp]\npop {r3,r4,r5,pc}\n");
}
