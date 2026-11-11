#include <stdint.h>
#include <stddef.h>
#include "native_lis_context.h"
struct r1_lis_context_prefix r1_lis_context __attribute__((section(".bss.r1.lis.context"),aligned(4)));
extern int32_t lis2dw12_fifo_data_level_get(const stmdev_ctx_t *,uint8_t *);
/* Strong replacement for the upstream weak read wrapper: native is unguarded
 * and captures handle before callback. The canonical native level call frame is reused. */
int32_t lis2dw12_read_reg(const stmdev_ctx_t *ctx, uint8_t reg,
                          uint8_t *data, uint16_t length)
{
 const volatile stmdev_ctx_t *live=ctx;
 void *handle=live->handle;
 stmdev_read_ptr callback=live->read_reg;
 return callback(handle,reg,data,length);
}
_Static_assert(offsetof(stmdev_ctx_t,read_reg)==4 &&
               offsetof(stmdev_ctx_t,handle)==12,"native ST read context fields");
int32_t r1_lis2dw12_fifo_burst_read(const stmdev_ctx_t *ctx,
                                  uint8_t *destination, uint32_t samples)
{
 /* Stock wraps the six-byte sample count to the transport's 16-bit length. */
 return lis2dw12_read_reg(ctx, 0x28, destination,
                         (uint16_t)(samples * UINT32_C(6)));
}
int32_t r1_lis2dw12_fifo_read(uint8_t *destination, uint32_t requested)
{
 uint8_t count = 0;
 const stmdev_ctx_t *ctx = (const stmdev_ctx_t *)&r1_lis_context;
 (void)lis2dw12_fifo_data_level_get(ctx, &count);
 if (count != 0) {
  if (count > requested)
   count = (uint8_t)requested;
  /* Stock ignores transport status and returns the selected sample count. */
  (void)r1_lis2dw12_fifo_burst_read(ctx, destination, count);
 }
 return count;
}
