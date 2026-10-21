#include <stdint.h>
#include <stddef.h>
struct r1_power_class {uint32_t link;char key[12];uint16_t tag,flags,size,reserved;uint32_t value;};
struct r1_dev_info_class {uint32_t link;char key[12];uint16_t tag,flags,size,reserved;uint32_t words[13];};
_Static_assert(sizeof(struct r1_power_class)==28 && offsetof(struct r1_power_class,value)==24,"power class layout");
_Static_assert(sizeof(struct r1_dev_info_class)==76 && offsetof(struct r1_dev_info_class,words)==24,"device info class layout");
struct r1_power_class r1_power_kv_class __attribute__((section(".r1.battery.kv.power"),aligned(4)))={.key="power",.tag=1,.flags=2,.size=4,.value=0};
struct r1_dev_info_class r1_dev_info_kv_class __attribute__((section(".r1.battery.kv.devinfo"),aligned(4)))={.key="dev_info",.tag=1,.size=52,.words={0,0,UINT32_MAX,UINT32_MAX,UINT32_MAX,0x484d4143,1,0,0,0,0,25,0}};
void *volatile r1_batcfg_record_kv_handle __attribute__((section(".r1.battery.kv.power.handle"),aligned(4)))=&r1_power_kv_class;
void *volatile r1_device_info_record_kv_handle __attribute__((section(".r1.battery.kv.devinfo.handle"),aligned(4)))=&r1_dev_info_kv_class;
