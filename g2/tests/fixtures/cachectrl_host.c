#define OPEN_CFW_CACHE_EVENT_READ 1U
#define OPEN_CFW_CACHE_EVENT_WRITE 2U
#define OPEN_CFW_CACHE_EVENT_DSB 3U
#define OPEN_CFW_CACHE_EVENT_ISB 4U

#define OPEN_CFW_CACHE_POWER_STATE_ADDRESS 0xE001E300U
#define OPEN_CFW_CACHE_CCR_ADDRESS 0xE000ED14U
#define OPEN_CFW_CACHE_ICIALLU_ADDRESS 0xE000EF50U
#define OPEN_CFW_CACHE_CSSELR_ADDRESS 0xE000ED84U
#define OPEN_CFW_CACHE_CCSIDR_ADDRESS 0xE000ED80U
#define OPEN_CFW_CACHE_DCISW_ADDRESS 0xE000EF60U
#define OPEN_CFW_CACHE_DCCSW_ADDRESS 0xE000EF6CU
#define OPEN_CFW_CACHE_DCCISW_ADDRESS 0xE000EF74U
#define OPEN_CFW_CACHE_DCIMVAC_ADDRESS 0xE000EF5CU
#define OPEN_CFW_CACHE_DCCIMVAC_ADDRESS 0xE000EF70U
#define OPEN_CFW_CACHE_DCCMVAC_ADDRESS 0xE000EF68U
#define OPEN_CFW_CACHE_PREFETCH_CONTROL_ADDRESS 0xE001E004U

unsigned int open_cfw_test_cache_power_state;
unsigned int open_cfw_test_cache_control;
unsigned int open_cfw_test_cache_icache_invalidate;
unsigned int open_cfw_test_cache_selector;
unsigned int open_cfw_test_cache_geometry;
unsigned int open_cfw_test_cache_dcisw;
unsigned int open_cfw_test_cache_dccsw;
unsigned int open_cfw_test_cache_dccisw;
unsigned int open_cfw_test_cache_dcimvac;
unsigned int open_cfw_test_cache_dccimvac;
unsigned int open_cfw_test_cache_dccmvac;
unsigned int open_cfw_test_cache_prefetch_control;
unsigned char open_cfw_test_cache_prefetch_config[3];
unsigned int open_cfw_test_cache_event_count;
unsigned int open_cfw_test_cache_event_kind[256];
unsigned int open_cfw_test_cache_event_address[256];
unsigned int open_cfw_test_cache_event_value[256];

static void open_cfw_test_cache_record(
    unsigned int kind,
    unsigned int address,
    unsigned int value
)
{
    unsigned int index = open_cfw_test_cache_event_count++;

    if (index < 256U) {
        open_cfw_test_cache_event_kind[index] = kind;
        open_cfw_test_cache_event_address[index] = address;
        open_cfw_test_cache_event_value[index] = value;
    }
}

void open_cfw_test_cache_reset(void)
{
    unsigned int index;

    open_cfw_test_cache_power_state = 0U;
    open_cfw_test_cache_control = 0U;
    open_cfw_test_cache_icache_invalidate = 0xFFFFFFFFU;
    open_cfw_test_cache_selector = 0xFFFFFFFFU;
    open_cfw_test_cache_geometry = 0U;
    open_cfw_test_cache_dcisw = 0xFFFFFFFFU;
    open_cfw_test_cache_dccsw = 0xFFFFFFFFU;
    open_cfw_test_cache_dccisw = 0xFFFFFFFFU;
    open_cfw_test_cache_dcimvac = 0xFFFFFFFFU;
    open_cfw_test_cache_dccimvac = 0xFFFFFFFFU;
    open_cfw_test_cache_dccmvac = 0xFFFFFFFFU;
    open_cfw_test_cache_prefetch_control = 0xFFFFFFFFU;
    open_cfw_test_cache_prefetch_config[0] = 6U;
    open_cfw_test_cache_prefetch_config[1] = 6U;
    open_cfw_test_cache_prefetch_config[2] = 4U;
    open_cfw_test_cache_event_count = 0U;
    for (index = 0U; index < 256U; ++index) {
        open_cfw_test_cache_event_kind[index] = 0U;
        open_cfw_test_cache_event_address[index] = 0U;
        open_cfw_test_cache_event_value[index] = 0U;
    }
}

unsigned int open_cfw_test_cache_read(unsigned int address)
{
    unsigned int value = 0U;

    switch (address) {
    case OPEN_CFW_CACHE_POWER_STATE_ADDRESS:
        value = open_cfw_test_cache_power_state;
        break;
    case OPEN_CFW_CACHE_CCR_ADDRESS:
        value = open_cfw_test_cache_control;
        break;
    case OPEN_CFW_CACHE_CCSIDR_ADDRESS:
        value = open_cfw_test_cache_geometry;
        break;
    default:
        break;
    }
    open_cfw_test_cache_record(
        OPEN_CFW_CACHE_EVENT_READ,
        address,
        value
    );
    return value;
}

void open_cfw_test_cache_write(
    unsigned int address,
    unsigned int value
)
{
    switch (address) {
    case OPEN_CFW_CACHE_CCR_ADDRESS:
        open_cfw_test_cache_control = value;
        break;
    case OPEN_CFW_CACHE_ICIALLU_ADDRESS:
        open_cfw_test_cache_icache_invalidate = value;
        break;
    case OPEN_CFW_CACHE_CSSELR_ADDRESS:
        open_cfw_test_cache_selector = value;
        break;
    case OPEN_CFW_CACHE_DCISW_ADDRESS:
        open_cfw_test_cache_dcisw = value;
        break;
    case OPEN_CFW_CACHE_DCCSW_ADDRESS:
        open_cfw_test_cache_dccsw = value;
        break;
    case OPEN_CFW_CACHE_DCCISW_ADDRESS:
        open_cfw_test_cache_dccisw = value;
        break;
    case OPEN_CFW_CACHE_DCIMVAC_ADDRESS:
        open_cfw_test_cache_dcimvac = value;
        break;
    case OPEN_CFW_CACHE_DCCIMVAC_ADDRESS:
        open_cfw_test_cache_dccimvac = value;
        break;
    case OPEN_CFW_CACHE_DCCMVAC_ADDRESS:
        open_cfw_test_cache_dccmvac = value;
        break;
    case OPEN_CFW_CACHE_PREFETCH_CONTROL_ADDRESS:
        open_cfw_test_cache_prefetch_control = value;
        break;
    default:
        break;
    }
    open_cfw_test_cache_record(
        OPEN_CFW_CACHE_EVENT_WRITE,
        address,
        value
    );
}

void open_cfw_test_cache_dsb(void)
{
    open_cfw_test_cache_record(OPEN_CFW_CACHE_EVENT_DSB, 0U, 0U);
}

void open_cfw_test_cache_isb(void)
{
    open_cfw_test_cache_record(OPEN_CFW_CACHE_EVENT_ISB, 0U, 0U);
}

#define OPEN_CFW_CACHE_READ(address) \
    open_cfw_test_cache_read(address)
#define OPEN_CFW_CACHE_WRITE(address, value) \
    open_cfw_test_cache_write(address, value)
#define OPEN_CFW_CACHE_PREFETCH_CONFIG \
    open_cfw_test_cache_prefetch_config
#define OPEN_CFW_CACHE_DSB() open_cfw_test_cache_dsb()
#define OPEN_CFW_CACHE_ISB() open_cfw_test_cache_isb()

#include "../../components/apollo_main/core_overlay/cachectrl.c"
