/* SPDX-License-Identifier: MIT */
#include <driver/gx_padmux.h>
extern int open_cfw_gx8002_padmux_get(int pad_id);
int open_cfw_gx8002_padmux_check(int pad_id, int function)
{
    if (pad_id < 0 || function < 0)
        return -1;
    unsigned char observed=(unsigned char)open_cfw_gx8002_padmux_get(pad_id);
    return observed == function ? 0 : -1;
}
