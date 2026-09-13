/* SPDX-License-Identifier: MIT
 * Application request/countdown processing, pending decoded qualification.
 */
#include <stdint.h>
extern uint32_t open_cfw_gx8002_i2s_app[8];
extern uint32_t open_cfw_gx8002_i2s_request;
extern uint8_t open_cfw_gx8002_i2s_mode_state;
extern void open_cfw_gx8002_i2s_poll(void);
extern void open_cfw_gx8002_i2s_acknowledge(void);
extern int open_cfw_gx8002_start_i2s(void);
extern void open_cfw_gx8002_stop_i2s(void);
extern void open_cfw_gx8002_i2s_lock(uint32_t);
extern void open_cfw_gx8002_i2s_unlock(uint32_t);
extern void open_cfw_gx8002_i2s_delay(uint32_t);
extern int printf(const char *,...);
const char open_cfw_gx8002_i2s_tick_request[] __attribute__((aligned(1)))="processing i2s status request, mode_state = %d\n";
const char open_cfw_gx8002_i2s_tick_lock[] __attribute__((aligned(1)))="====  I2S output requested, lock ====\n";
const char open_cfw_gx8002_i2s_tick_unlock[] __attribute__((aligned(1)))="====  I2S output requested, unlock ====\n";
const char open_cfw_gx8002_i2s_tick_timeout[] __attribute__((aligned(1)))="[YW_APP]UART wakeup timeout, unlock\n";
int open_cfw_gx8002_i2s_request_tick(void)
{
    open_cfw_gx8002_i2s_poll();
    if(open_cfw_gx8002_i2s_request==1){
        printf(open_cfw_gx8002_i2s_tick_request,open_cfw_gx8002_i2s_mode_state);
        uint32_t mode=open_cfw_gx8002_i2s_mode_state;
        if(mode==1){
            open_cfw_gx8002_i2s_lock(open_cfw_gx8002_i2s_app[2]);
            printf(open_cfw_gx8002_i2s_tick_lock);open_cfw_gx8002_start_i2s();
            open_cfw_gx8002_i2s_acknowledge();open_cfw_gx8002_i2s_request=0;
        }else if(mode==0){
            open_cfw_gx8002_stop_i2s();open_cfw_gx8002_i2s_acknowledge();
            open_cfw_gx8002_i2s_request=0;
            open_cfw_gx8002_i2s_unlock(open_cfw_gx8002_i2s_app[2]);
            printf(open_cfw_gx8002_i2s_tick_unlock);open_cfw_gx8002_i2s_delay(13);
        }
    }
    if((int32_t)open_cfw_gx8002_i2s_app[3]>0){
        open_cfw_gx8002_i2s_app[3]-=10;
        if((int32_t)open_cfw_gx8002_i2s_app[3]<=0 && !open_cfw_gx8002_i2s_app[5]){
            printf(open_cfw_gx8002_i2s_tick_timeout);
            open_cfw_gx8002_i2s_unlock(open_cfw_gx8002_i2s_app[2]);
            open_cfw_gx8002_i2s_app[3]=0;
        }
    }
    return 0;
}
