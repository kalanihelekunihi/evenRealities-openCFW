/* Stock 0x4f650: EAT logging mode and threshold command. */
#include <stdint.h>

extern int32_t r1_native_sscanf(const char *input,const char *format,...);
extern void r1_structured_log_threshold_set(uint32_t level);
extern void r1_structured_log_mode_set(uint32_t mode);
extern void r1_eat_respond_format(const char *format,...);

void r1_eat_callback_0004f650(char *argument)
{
    uint32_t mode=0u,requested_level=0u;
    if(r1_native_sscanf(argument,"%d %d",&mode,&requested_level)!=2){
        r1_eat_respond_format(
            "ERROR: Invalid parameter format. Use: AT^LOG=0|1|2\r\n");
        return;
    }
    r1_structured_log_threshold_set((uint8_t)requested_level>=4u?4u:3u);
    mode=(uint8_t)mode;
    if(mode!=1u && mode!=2u && mode!=4u){
        r1_eat_respond_format("ERROR TYPE");
        return;
    }
    r1_structured_log_mode_set(mode);
    r1_eat_respond_format("OK");
}
