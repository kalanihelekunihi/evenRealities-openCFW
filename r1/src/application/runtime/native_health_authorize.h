#ifndef R1_NATIVE_HEALTH_AUTHORIZE_H
#define R1_NATIVE_HEALTH_AUTHORIZE_H
#include <stdint.h>
struct r1_health_auth_parameters {
    const void *key;
    const char *uuid;
    uint8_t uuid_length,padding[3];
    uint32_t timestamp;
};
extern const void *volatile r1_health_authorization_cached_key;
int32_t r1_health_authorization_key_read(void *,uint32_t,uint32_t,uint32_t);
uint32_t r1_health_auth_parameters_set(const struct r1_health_auth_parameters *);
uint32_t r1_health_lifecycle_authorize_native(void);
#endif
