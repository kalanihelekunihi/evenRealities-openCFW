#ifndef R1_NATIVE_LIS_CONTEXT_H
#define R1_NATIVE_LIS_CONTEXT_H
#include <stddef.h>
#include "lis2dw12_reg.h"

/* Stock owns only this 16-byte prefix. The pinned ST context additionally
 * declares a private pointer, which the reconstructed entries do not access. */
struct r1_lis_context_prefix {
 stmdev_write_ptr write;
 stmdev_read_ptr read;
 stmdev_mdelay_ptr delay;
 void *handle;
};
_Static_assert(sizeof(struct r1_lis_context_prefix)==16 &&
               offsetof(struct r1_lis_context_prefix,write)==0 &&
               offsetof(struct r1_lis_context_prefix,read)==4 &&
               offsetof(struct r1_lis_context_prefix,delay)==8 &&
               offsetof(struct r1_lis_context_prefix,handle)==12,
               "native LIS context prefix");
extern struct r1_lis_context_prefix r1_lis_context;
#endif
