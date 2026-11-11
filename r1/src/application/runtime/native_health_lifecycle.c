/* Instruction-led reconstruction of stock 0x4bd98..0x4c097. */
#include "native_health_lifecycle.h"
#include "native_crash_recovery.h"
#include "native_health_storage.h"
#include "native_health_profile.h"
#include "native_health_authorize.h"
#include "native_health_engine_modes.h"
#include "native_gomore_authorization.h"
#include <stddef.h>
extern uint32_t gomore_primitives_size_736(void),gomore_primitives_size_14816(void);
extern uint32_t r1_health_lifecycle_engine_initialize_native(uint32_t,uint32_t,const void *,void *);
extern uint32_t r1_gomore_authorization_dispatch_native(uint32_t,uint32_t);
extern void gomore_primitives_noop_91080(void);
extern uint32_t r1_time_backend_timestamp(void),r1_subscriber_register(uint32_t,uint32_t,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern void __aeabi_memclr(void *,size_t);
extern void *r1_native_memory_move(void *,const void *,size_t);
extern volatile uint8_t r1_crash_payload[736];
/* Stock placed the engine and output records at fixed RAM addresses. The
 * source link allocates unrelated state there, so this lifecycle owns the
 * corresponding buffers and passes their addresses to the C engine. */
#define FLAGS ((volatile uint8_t *)&r1_gomore_authorization_state)
volatile uint8_t r1_gomore_engine_storage[14816] __attribute__((aligned(4)));
volatile uint8_t r1_gomore_output_records[4][100] __attribute__((aligned(4)));
volatile uint8_t r1_gomore_output_extra[100] __attribute__((aligned(4)));
volatile uint32_t r1_gomore_output_descriptor[66] __attribute__((aligned(4)));
#define DESCRIPTOR r1_gomore_output_descriptor
static const float default_profile[7]={28.0f,1.0f,175.0f,75.0f,-1.0f,-1.0f,-1.0f};
static void report(uint32_t marker,uint32_t id,const char *structured,const char *plain,uint32_t value,uint32_t count) {
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u)) {
        if (count) (void)r1_structured_log_format(marker,structured,structured,value);
        else (void)r1_structured_log_format(marker,structured,structured);
    }
    if (r1_structured_log_mode_get()&2u) {
        if (count) nrf_log_frontend_std_1(id,plain,value);
        else nrf_log_frontend_std_0(id,plain);
    }
}
void r1_native_gomore_lifecycle_initialize(uint32_t mode) {
    uint32_t profile[7],previous_header[17];
    volatile uint16_t recovered_length;
    void *previous=(void *)(uintptr_t)r1_crash_payload;
    uint32_t previous_size=gomore_primitives_size_736();
    uint32_t engine_size=gomore_primitives_size_14816();
    static const char sizes[]="[RING]gm mem size:%d, previous size:%d";
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c800000u,sizes,sizes,engine_size,previous_size);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_2(0x1c0003u,"gm mem size:%d, previous size:%d",engine_size,previous_size);
    FLAGS[4]=0;
    uint32_t status=r1_health_lifecycle_authorize_native();
    if (status) {
        report(0x04400000u,0x1c0001u,"[RING]gomore setAuthParameters failed:%d","gomore setAuthParameters failed:%d",status,1);
        FLAGS[5]=1;FLAGS[4]=1;
        status=r1_health_lifecycle_authorize_native();
        if (status) {
            report(0x04400000u,0x1c0001u,"[RING]gomore setAuth failed: %d","gomore setAuth failed: %d",status,1);
            return;
        }
        FLAGS[4]=0;
    }
    __aeabi_memclr(previous_header,68);
    if (!(uint32_t)r1_health_lifecycle_restore_native(previous_header,64,previous,736)) {
        __aeabi_memclr(previous,736);
        report(0x04000000u,0x1c0001u,"[RING]gm previousData not found, use default","gm previousData not found, use default",0,0);
    }
    if (mode==0 && r1_health_crash_record_magic_probe()) {
        recovered_length=0;
        uint32_t blob=r1_health_crash_provider_blob_accessor(&recovered_length);
        if (blob && recovered_length==736) {
            (void)r1_native_memory_move(previous,(const void *)(uintptr_t)blob,recovered_length);
            (void)r1_health_crash_provider_blob_clear();
            report(0x0c000000u,0x1c0003u,"[RING]gm crash previousData restore success","gm crash previousData restore success",0,0);
        }
    }
    __aeabi_memclr(profile,28);
    if (!(uint32_t)r1_health_lifecycle_profile_native(profile,0,0,0)) {
        (void)r1_native_memory_move(profile,default_profile,28);
        report(0x04000000u,0x1c0001u,"[RING]gm user info not set, use default","gm user info not set, use default",0,0);
    }
    if (mode==1) __aeabi_memclr(previous,736);
    uint32_t timestamp=r1_time_backend_timestamp();
    status=r1_health_lifecycle_engine_initialize_native(
        (uint32_t)(uintptr_t)r1_gomore_engine_storage,timestamp,profile,previous);
    if (status) {
        report(0x04400000u,0x1c0001u,"[RING]gomore healthIndexInitUser failed:%d","gomore healthIndexInitUser failed:%d",status,1);
        if (status!=UINT32_C(0xfffffffb)) return;
        __aeabi_memclr(previous,736);
        status=r1_health_lifecycle_engine_initialize_native(
            (uint32_t)(uintptr_t)r1_gomore_engine_storage,timestamp,profile,previous);
        if (status) {
            report(0x04400000u,0x1c0001u,"[RING]gomore init failed:%d","gomore init failed:%d",status,1);
            return;
        }
    }
    FLAGS[0]=1;
    __aeabi_memclr((void *)(uintptr_t)DESCRIPTOR,264);
    DESCRIPTOR[2]=(uint32_t)(uintptr_t)r1_gomore_output_records[0];
    DESCRIPTOR[3]=(uint32_t)(uintptr_t)r1_gomore_output_records[1];
    DESCRIPTOR[4]=(uint32_t)(uintptr_t)r1_gomore_output_records[2];
    DESCRIPTOR[6]=(uint32_t)(uintptr_t)r1_gomore_output_records[3];
    DESCRIPTOR[8]=(uint32_t)(uintptr_t)r1_gomore_output_extra;
    (void)r1_health_lifecycle_profile_apply_native(1,0,0);
    (void)r1_health_lifecycle_mode_native(1,0x66);
    if (!FLAGS[2]) FLAGS[2]=(uint8_t)r1_subscriber_register(0,(uint32_t)(uintptr_t)r1_gomore_time_transition_adapter,0x20006610u);
    report(0x0c400000u,0x1c0003u,"[RING]gm healthIndexInitUser success, timestamp:%d","gm healthIndexInitUser success, timestamp:%d",timestamp,1);
}

/* Stock 0x4c37c, a separate entry merged into the initializer's dossier. */
void r1_gomore_force_reinitialize_native(void) {
    if (r1_gomore_wake_authorization_flags & 1u)
        (void)r1_gomore_authorization_dispatch_native(4,0);
    /* Stock 0x91080 is a no-op; its discarded R0 is not a C argument. */
    gomore_primitives_noop_91080();
    __aeabi_memclr((void *)(uintptr_t)r1_crash_payload,736);
    r1_native_gomore_lifecycle_initialize(1);
}
/* The profile-change and idle-failure paths call this same stock entry.
 * Bind their historical seam name to the canonical implementation. */
extern __typeof__(r1_gomore_force_reinitialize_native) r1_record12_reinitialize
    __attribute__((alias("r1_gomore_force_reinitialize_native")));

/* Stock 0x5dc08: ignore NULL, forward/equal time and backward gaps <180. */
void r1_gomore_time_transition_adapter(uint32_t packet) {
    if (!packet) return;
    uint32_t newer=*(const volatile uint32_t *)(uintptr_t)(packet+8u);
    uint32_t older=*(const volatile uint32_t *)(uintptr_t)(packet+4u);
    if (newer>=older || older-newer<180u) return;
    report(0x0c000000u,0x1c0003u,"[RING]gm ts change, reinit algorithm",
        "gm ts change, reinit algorithm",0,0);
    r1_gomore_force_reinitialize_native();
}
