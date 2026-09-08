/* SPDX-License-Identifier: MIT */
#include <driver/gx_padmux.h>
typedef __UINTPTR_TYPE__ uintptr_t;
int open_cfw_gx8002_padmux_get(int pad_id)
{
    if ((unsigned int)pad_id > 32u)
        return -1;
    volatile unsigned int *words=(void *)(uintptr_t)0xa0010090u;
    unsigned int word=words[(unsigned int)pad_id/8u];
    return (word>>(((unsigned int)pad_id%8u)*4u))&15u;
}
