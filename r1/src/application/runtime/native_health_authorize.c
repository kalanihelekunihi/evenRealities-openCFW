/* Stock 0x6b27c: identity/key admission before health engine startup. */
#include "native_health_authorize.h"
#include <stddef.h>
extern void __aeabi_memclr(void *,size_t);
extern void r1_native_device_id_read_boundary(void *);
extern uint32_t r1_time_backend_timestamp(void);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
_Static_assert(sizeof(struct r1_health_auth_parameters)==16 && offsetof(struct r1_health_auth_parameters,uuid_length)==8 && offsetof(struct r1_health_auth_parameters,timestamp)==12,"stock auth descriptor");
static void note(uint32_t marker,uint32_t id,const char *structured,const char *plain,uint32_t value,unsigned count)
{
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u)) {
        if (count) (void)r1_structured_log_format(marker,structured,structured,value);
        else (void)r1_structured_log_format(marker,structured,structured);
    }
    if (r1_structured_log_mode_get()&2u) {
        if (count) nrf_log_frontend_std_1(id,plain,value);
        else nrf_log_frontend_std_0(id,plain);
    }
}
uint32_t r1_health_lifecycle_authorize_native(void)
{
    char uuid[28];uint8_t key[68];
    __aeabi_memclr(uuid,sizeof uuid);
    __aeabi_memclr(key,sizeof key);
    struct r1_health_auth_parameters parameters={0};
    r1_native_device_id_read_boundary(uuid);
    note(0x0c400000u,0x1c0003u,"[RING]gm device_uuid: %s","gm device_uuid: %s",(uint32_t)(uintptr_t)uuid,1);
    int32_t status=r1_health_authorization_key_read(key,64,0,0);
    if (status<0) {
        note(0x04400000u,0x1c0001u,"[RING]gomore get pkey failed: %d","gomore get pkey failed: %d",(uint32_t)status,1);
        return UINT32_MAX;
    }
    note(0x0c400000u,0x1c0003u,"[RING]gm pkey: %s","gm pkey: %s",(uint32_t)(uintptr_t)key,1);
    parameters.key=key;parameters.uuid=uuid;
    const volatile char *cursor=uuid;
    while (*cursor) ++cursor;
    parameters.uuid_length=(uint8_t)(cursor-uuid);
    parameters.timestamp=r1_time_backend_timestamp();
    uint32_t result=r1_health_auth_parameters_set(&parameters);
    if (result)
        note(0x04400000u,0x1c0001u,"[RING]gomore setAuthParameters failed: %d","gomore setAuthParameters failed: %d",result,1);
    else
        note(0x0c000000u,0x1c0003u,"[RING]gm set pkey success","gm set pkey success",0,0);
    return result;
}
