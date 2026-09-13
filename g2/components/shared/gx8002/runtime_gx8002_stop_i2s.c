/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern uint32_t open_cfw_gx8002_i2s_app[8];
extern uint8_t open_cfw_gx8002_i2s_pending;
extern int printf(const char *,...);
extern void open_cfw_gx8002_i2s_padmux(uint32_t,uint32_t);
extern void open_cfw_gx8002_i2s_close(uint32_t);
extern void open_cfw_gx8002_i2s_shutdown(void);
extern const char open_cfw_gx8002_start_i2s_log[],open_cfw_gx8002_start_i2s_close_log[];
const char open_cfw_gx8002_stop_i2s_name[] __attribute__((aligned(1)))="close_i2s";
void open_cfw_gx8002_stop_i2s(void)
{
    printf(open_cfw_gx8002_start_i2s_log,open_cfw_gx8002_stop_i2s_name,307);
    if(!open_cfw_gx8002_i2s_app[5])return;
    open_cfw_gx8002_i2s_app[5]=0;open_cfw_gx8002_i2s_pending=0;
    open_cfw_gx8002_i2s_padmux(7,1);open_cfw_gx8002_i2s_padmux(8,1);
    open_cfw_gx8002_i2s_padmux(9,1);open_cfw_gx8002_i2s_padmux(10,1);
    if(open_cfw_gx8002_i2s_app[1]!=UINT32_MAX){
        printf(open_cfw_gx8002_start_i2s_close_log,open_cfw_gx8002_stop_i2s_name,329,open_cfw_gx8002_i2s_app[1]);
        open_cfw_gx8002_i2s_close(open_cfw_gx8002_i2s_app[1]);
        open_cfw_gx8002_i2s_shutdown();open_cfw_gx8002_i2s_app[1]=UINT32_MAX;
    }
    open_cfw_gx8002_i2s_app[6]=0;open_cfw_gx8002_i2s_app[7]=0;open_cfw_gx8002_i2s_app[0]=0;
}
