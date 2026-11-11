/* Stock 0x6fea0: GoMore engine initialization at the firmware ABI. */
#include <stdint.h>
#include <stddef.h>
#include "../../vendor/gomore_primitives/gomore_primitives.h"
#include "native_gomore_runtime_configuration.h"

extern volatile uint32_t r1_gomore_native_context;
extern void r1_native_srand(uint32_t);
extern uint32_t r1_native_rand(void);
extern int32_t r1_gomore_runtime_validate_native(uint32_t,uint32_t);
extern uint32_t r1_gomore_native_engine_profile_convert(const void *,void *);
extern uint32_t r1_gomore_filter_configure_native(uint32_t,uint32_t,uint32_t,uint32_t);
extern void r1_gomore_log_native(uint32_t,uint32_t,const char *,...);

static int32_t random_value(void)
{ return (int32_t)r1_native_rand(); }

static void small_filter(void *record,uint32_t mode,uint32_t count,float cutoff)
{
    (void)r1_gomore_filter_configure_native((uint32_t)(uintptr_t)record,
        mode,count,(uint32_t)(uintptr_t)&cutoff);
}

static void large_filter(void *record,uint32_t count,const float parameters[2])
{
    (void)r1_gomore_filter_configure_native((uint32_t)(uintptr_t)record,
        2u,count,(uint32_t)(uintptr_t)parameters);
}

static void initialize_filter(void *record,uint32_t mode,uint32_t count,
                              const float parameters[2])
{
    (void)r1_gomore_filter_configure_native((uint32_t)(uintptr_t)record,
        mode,count,(uint32_t)(uintptr_t)parameters);
}

static void finish_sps_initialize(void *record)
{
    uint8_t *bytes=record;
    uint32_t source_address=*(const volatile uint32_t *)(bytes+0x40u);
    (void)gomore_primitives_sps_refresh_affine_pairs(
        (const float *)(uintptr_t)source_address,
        (float *)(void *)(bytes+0x18u),
        (uint32_t *)(void *)(bytes+0x20u),
        (float *)(void *)(bytes+0x34u),
        (uint32_t *)(void *)(bytes+0x3cu));
}

static int32_t native_profile_convert(const void *profile,void *state)
{ return (int32_t)r1_gomore_native_engine_profile_convert(profile,state); }

static void native_log_u32(uint32_t level,uint32_t category,
                           const char *format,uint32_t value)
{ r1_gomore_log_native(level,category,format,value); }

uint32_t r1_health_lifecycle_engine_initialize_native(uint32_t engine,
    uint32_t timestamp,const void *profile,void *previous)
{
    r1_gomore_native_context=engine;
    gomore_primitives_sleep_algorithm_configuration configuration={
        .random_seed=r1_gomore_runtime_configuration.random_seed,
        .time_configuration=(uint8_t *)previous+0x298u,
        .time_configuration_length=736u-0x298u,
        .seed_random=r1_native_srand,
        .random_value=random_value,
        .initialize_small_filter=small_filter,
        .initialize_large_filter=large_filter,
        .finish_sps_initialize=finish_sps_initialize,
        .initialize_filter=initialize_filter,
        .native_runtime_validate=r1_gomore_runtime_validate_native,
        .native_log_u32=native_log_u32,
        .native_profile_convert=native_profile_convert,
    };
    gomore_primitives_sleep_algorithm_outputs outputs={0};
    return (uint32_t)gomore_primitives_sleep_algorithm_initialize(
        (void *)(uintptr_t)engine,14816u,timestamp,
        (const gomore_primitives_profile_input *)profile,
        previous,736u,(uint32_t)(uintptr_t)previous,
        &configuration,&outputs);
}
