/* SPDX-License-Identifier: MIT
 * Recovered application I2S start path. Candidate pending decoded qualification.
 */
#include <stdint.h>
extern uint32_t open_cfw_gx8002_i2s_app[8];
extern uint8_t open_cfw_gx8002_i2s_pending;
extern int printf(const char *,...);
extern void open_cfw_gx8002_i2s_close(uint32_t);
extern void open_cfw_gx8002_i2s_shutdown(void);
extern void open_cfw_gx8002_i2s_padmux(uint32_t,uint32_t);
extern void open_cfw_gx8002_i2s_clock_set(uint32_t,uint32_t);
extern void open_cfw_gx8002_i2s_initialize(uint32_t);
extern uint32_t open_cfw_gx8002_i2s_clock_get(uint32_t);
extern uint32_t open_cfw_gx8002_i2s_open(uint32_t);
extern void open_cfw_gx8002_i2s_callback(uint32_t,const void *);
extern void open_cfw_gx8002_i2s_mode(uint32_t,uint32_t);
extern int32_t open_cfw_gx8002_i2s_buffer_size(void);
extern void open_cfw_gx8002_i2s_channel(uint32_t,uint32_t);
extern uint32_t open_cfw_gx8002_i2s_buffer_base(void);
extern void open_cfw_gx8002_i2s_buffers(uint32_t,const void *);
extern void open_cfw_gx8002_i2s_format(uint32_t,const void *);
extern int open_cfw_gx8002_next_range(uint32_t,uint32_t);
extern const char open_cfw_gx8002_start_i2s_name[],open_cfw_gx8002_start_i2s_log[],open_cfw_gx8002_start_i2s_close_log[],open_cfw_gx8002_start_i2s_mclk[],open_cfw_gx8002_start_i2s_lrclk[],open_cfw_gx8002_start_i2s_bits[],open_cfw_gx8002_start_i2s_master[],open_cfw_gx8002_start_i2s_done[];
int open_cfw_gx8002_start_i2s(void)
{
    printf(open_cfw_gx8002_start_i2s_log,open_cfw_gx8002_start_i2s_name,277);
    if(open_cfw_gx8002_i2s_app[5])return -1;
    open_cfw_gx8002_i2s_app[5]=1;open_cfw_gx8002_i2s_pending=1;
    if(open_cfw_gx8002_i2s_app[1]!=UINT32_MAX){
        printf(open_cfw_gx8002_start_i2s_close_log,open_cfw_gx8002_start_i2s_name,290,open_cfw_gx8002_i2s_app[1]);
        open_cfw_gx8002_i2s_close(open_cfw_gx8002_i2s_app[1]);open_cfw_gx8002_i2s_shutdown();open_cfw_gx8002_i2s_app[1]=UINT32_MAX;
    }
    open_cfw_gx8002_i2s_padmux(7,3);open_cfw_gx8002_i2s_padmux(8,3);open_cfw_gx8002_i2s_padmux(9,3);open_cfw_gx8002_i2s_padmux(10,3);
    open_cfw_gx8002_i2s_clock_set(8,5);open_cfw_gx8002_i2s_initialize(0);
    struct {uint32_t rate;uint8_t channels,bits,mode,polarity;uint32_t clock;} format;
    format.clock=open_cfw_gx8002_i2s_clock_get(11);
    uint32_t handle=open_cfw_gx8002_i2s_open(0);open_cfw_gx8002_i2s_app[1]=handle;
    struct {int (*callback)(uint32_t,uint32_t);void *context;} callback={open_cfw_gx8002_next_range,0};
    open_cfw_gx8002_i2s_callback(handle,&callback);
    open_cfw_gx8002_i2s_mode(open_cfw_gx8002_i2s_app[1],0);
    open_cfw_gx8002_i2s_app[0]=open_cfw_gx8002_i2s_buffer_size()/2;
    open_cfw_gx8002_i2s_channel(open_cfw_gx8002_i2s_app[1],0);
    open_cfw_gx8002_i2s_app[6]=open_cfw_gx8002_i2s_buffer_base();
    open_cfw_gx8002_i2s_app[7]=open_cfw_gx8002_i2s_buffer_base()+open_cfw_gx8002_i2s_app[0];
    format.channels=2;
    uint32_t buffers[3]={open_cfw_gx8002_i2s_app[6],open_cfw_gx8002_i2s_app[7],open_cfw_gx8002_i2s_app[0]};
    open_cfw_gx8002_i2s_buffers(open_cfw_gx8002_i2s_app[1],buffers);
    format.rate=16000;format.bits=16;format.mode=0;format.polarity=0;
    open_cfw_gx8002_i2s_format(open_cfw_gx8002_i2s_app[1],&format);
    printf(open_cfw_gx8002_start_i2s_mclk,open_cfw_gx8002_i2s_clock_get(11));
    printf(open_cfw_gx8002_start_i2s_lrclk,format.rate);printf(open_cfw_gx8002_start_i2s_bits,format.bits);
    printf(open_cfw_gx8002_start_i2s_done,open_cfw_gx8002_start_i2s_master);return 0;
}
