#include <stdint.h>
extern uint32_t r1_yhm_register_read_native(uint32_t,uint32_t,uint8_t *);
extern uint32_t r1_yhm_register_write_native(uint32_t,uint32_t,const uint8_t *);
extern uint32_t r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
const char r1_yhm_system_track_ring[] __attribute__((section(".r1.yhm_track.ring")))="[RING]YHM2710_set_sys_track txdata = 0x%02x";
const char r1_yhm_system_track_sdk[] __attribute__((section(".r1.yhm_track.sdk")))="YHM2710_set_sys_track txdata = 0x%02x";
/* Native saves incoming r2/r3 as two words, replacing only their low bytes.
 * Keep the selected target register boundary explicit and out of line. */
__attribute__((noinline)) uint32_t r1_yhm_system_track_native(void)
{
    uint32_t incoming2,incoming3;
    __asm__ volatile("mov %0, r2\nmov %1, r3" : "=r"(incoming2),"=r"(incoming3) : : "r2","r3");
    volatile uint32_t read_word=incoming3&0xffffff00u,write_word=incoming2;
    (void)r1_yhm_register_read_native(1,1,(uint8_t *)&read_word);
    write_word=(write_word&0xffffff00u)|(((const volatile uint8_t *)&read_word)[0]|2u);
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x0c400000,r1_yhm_system_track_ring,r1_yhm_system_track_ring,(uint32_t)((const volatile uint8_t *)&write_word)[0]);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,r1_yhm_system_track_sdk,((const volatile uint8_t *)&write_word)[0]);
    uint32_t result=r1_yhm_register_write_native(1,1,(const uint8_t *)&write_word);
    uint32_t restored2=write_word,restored3=read_word;
    __asm__ volatile("mov r2, %0\nmov r3, %1" : : "r"(restored2),"r"(restored3) : "r2","r3");
    return result;
}
uint32_t r1_native_charger_initialize(void)
{ return r1_yhm_system_track_native(); }
