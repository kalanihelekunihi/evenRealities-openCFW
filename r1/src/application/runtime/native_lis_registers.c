/* Native write transport in C. Capture the handle before the callback pointer,
 * with no added null guard. Exact compiler/spill identity is not established. */
#include <stddef.h>
#include "lis2dw12_reg.h"
_Static_assert(offsetof(stmdev_ctx_t,write_reg)==0 &&
               offsetof(stmdev_ctx_t,handle)==12,"native ST write context fields");
int32_t lis2dw12_write_reg(const stmdev_ctx_t *ctx, uint8_t reg,
                           uint8_t *data, uint16_t length)
{
 const volatile stmdev_ctx_t *live=ctx;
 void *handle=live->handle;
 stmdev_write_ptr callback=live->write_reg;
 return callback(handle,reg,data,length);
}
