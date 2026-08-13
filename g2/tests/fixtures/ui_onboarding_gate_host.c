unsigned int open_cfw_test_onboarding_result[3];
unsigned int open_cfw_test_onboarding_count[3];
unsigned int open_cfw_test_onboarding_order[3];
unsigned int open_cfw_test_onboarding_order_count;

static unsigned int open_cfw_test_onboarding_query(unsigned int index)
{
    ++open_cfw_test_onboarding_count[index];
    open_cfw_test_onboarding_order[
        open_cfw_test_onboarding_order_count++
    ] = index;
    return open_cfw_test_onboarding_result[index];
}

unsigned int open_cfw_test_onboarding_primary(void)
{
    return open_cfw_test_onboarding_query(0U);
}

unsigned int open_cfw_test_onboarding_secondary(void)
{
    return open_cfw_test_onboarding_query(1U);
}

unsigned int open_cfw_test_onboarding_tertiary(void)
{
    return open_cfw_test_onboarding_query(2U);
}

#define OPEN_CFW_UI_ONBOARDING_STATE_PRIMARY \
    open_cfw_test_onboarding_primary
#define OPEN_CFW_UI_ONBOARDING_STATE_SECONDARY \
    open_cfw_test_onboarding_secondary
#define OPEN_CFW_UI_ONBOARDING_STATE_TERTIARY \
    open_cfw_test_onboarding_tertiary

#include "../../components/apollo_main/core_overlay/ui_onboarding_gate.c"
