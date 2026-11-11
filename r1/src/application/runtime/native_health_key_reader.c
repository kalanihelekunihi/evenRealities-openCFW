/* Stock 0x6ad28: cached or FAL-loaded 64-byte authorization key. */
#include "native_health_authorize.h"
#include "native_health_storage.h"
#include "native_gomore_authorization.h"
#include <stddef.h>
/* Non-executable cold key text, referenced by the stock scatter-initialized pointer. */
const char r1_health_authorization_cold_key[65]
    __attribute__((section(".r1.health.auth.key.text")))="dAf331AQR+EPsRr09s4c1VANtru/UIZ5qY7GVLDX/ww9aWhk8MWdNKvKRjKbs7FL";
const void *volatile r1_health_authorization_cached_key
    __attribute__((section(".r1.health.auth.key.pointer"),aligned(4)))=r1_health_authorization_cold_key;
extern void *r1_native_memory_move(void *,const void *,size_t);
int32_t r1_health_authorization_key_read(void *destination,uint32_t ignored_length,uint32_t seed0,uint32_t seed1)
{
    (void)ignored_length;
    uint8_t scratch[64];
    const void *source;
    if (r1_gomore_authorization_state.device_id_cached_valid)
        source=r1_health_authorization_cached_key;
    else {
        if (!(uint32_t)r1_health_pkey_load_native(scratch,64,seed0,seed1)) return -2;
        source=scratch;
    }
    (void)r1_native_memory_move(destination,source,64);
    return 64;
}
