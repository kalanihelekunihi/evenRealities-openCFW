#include <stdint.h>
#include <stddef.h>
#define HEAD uint32_t link;char key[12];uint16_t tag,flags,size,reserved
struct nv_ble_class {HEAD;uint8_t payload[90];};
struct nv_health_class {HEAD;uint16_t words[6];};
struct nv_hsync_class {HEAD;uint8_t payload[24];};
struct nv_size_class {HEAD;uint8_t payload;};
_Static_assert(sizeof(struct nv_ble_class)==116 && sizeof(struct nv_health_class)==36 && sizeof(struct nv_hsync_class)==48 && sizeof(struct nv_size_class)==28,"native padded class extents");
struct nv_ble_class r1_nv_ble_mult_class __attribute__((section(".r1.nv.class.ble_mult"),aligned(4)))={.key="ble_mult",.tag=1,.size=90};
struct nv_health_class r1_nv_health_class __attribute__((section(".r1.nv.class.health"),aligned(4)))={.key="health",.tag=1,.size=12,.words={20,0x41af,200,50,200,0}};
struct nv_hsync_class r1_nv_hsync_class __attribute__((section(".r1.nv.class.hsync"),aligned(4)))={.key="hsync",.tag=1,.size=24};
struct nv_size_class r1_nv_r_size_class __attribute__((section(".r1.nv.class.r_size"),aligned(4)))={.key="r_size",.tag=1,.flags=2,.size=1};
void *volatile r1_ble_mult_kv_handle __attribute__((section(".r1.nv.ble_mult.handle"),aligned(4)))=&r1_nv_ble_mult_class;
void *volatile r1_health_settings_kv_handle __attribute__((section(".r1.nv.health.handle"),aligned(4)))=&r1_nv_health_class;
void *volatile r1_health_record_kv_handle __attribute__((section(".r1.nv.hsync.handle"),aligned(4)))=&r1_nv_hsync_class;
void *volatile r1_r_size_kv_handle __attribute__((section(".r1.nv.r_size.handle"),aligned(4)))=&r1_nv_r_size_class;
