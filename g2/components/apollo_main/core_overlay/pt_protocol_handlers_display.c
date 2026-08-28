/* SPDX-License-Identifier: MIT */
#include "pt_protocol_handlers_display.h"

static int open_cfw_pt_display_valid(const uint8_t *r, uint8_t n, uint8_t min)
{ return r != NULL && n >= min; }

static int open_cfw_pt_display_mode(
    const struct open_cfw_pt_display_providers *providers)
{
    uint8_t mode;
    if (providers == NULL || providers->get_product_mode == NULL ||
        providers->get_product_mode(&mode, providers->context) != 0) return -1;
    return mode == 1U ? 1 : 0;
}

static int open_cfw_pt_display_screen(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l,
    const struct open_cfw_pt_display_providers *providers,
    uint16_t screen_id, int enabled, uint8_t response_command)
{
    int mode;
    uint8_t result = 5U;
    if (!open_cfw_pt_display_valid(r, n, 4U)) return OPEN_CFW_PT_INVALID_ARGUMENT;
    mode = open_cfw_pt_display_mode(providers);
    if (mode < 0) return OPEN_CFW_PT_HANDLER_FAILED;
    if (mode == 1 && providers->set_test_screen != NULL)
        result = providers->set_test_screen(
            screen_id, enabled, providers->context) == 0 ? 0U : 1U;
    return open_cfw_pt_make_status_payload(response_command, result, 3U, p, l);
}

#define OPEN_CFW_PT_DISPLAY_SCREEN_HANDLER(name,id,on,response) \
static int name(const uint8_t *r,uint8_t n,uint8_t *p,uint8_t *l,void *c) \
{ return open_cfw_pt_display_screen(r,n,p,l,c,id,on,response); }

OPEN_CFW_PT_DISPLAY_SCREEN_HANDLER(open_cfw_pt_display_20,0x010BU,1,0x25U)
OPEN_CFW_PT_DISPLAY_SCREEN_HANDLER(open_cfw_pt_display_22,0x010BU,0,0x26U)
OPEN_CFW_PT_DISPLAY_SCREEN_HANDLER(open_cfw_pt_display_6e,0x010FU,1,0x6DU)
OPEN_CFW_PT_DISPLAY_SCREEN_HANDLER(open_cfw_pt_display_74,0x010FU,0,0x6EU)
OPEN_CFW_PT_DISPLAY_SCREEN_HANDLER(open_cfw_pt_display_75,0x0110U,1,0x74U)
OPEN_CFW_PT_DISPLAY_SCREEN_HANDLER(open_cfw_pt_display_77,0x0110U,0,0x75U)

static int open_cfw_pt_display_2d(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_display_providers *providers = c;
    int mode;
    uint8_t result = 5U;
    if (!open_cfw_pt_display_valid(r, n, 9U)) return OPEN_CFW_PT_INVALID_ARGUMENT;
    mode = open_cfw_pt_display_mode(providers);
    if (mode < 0) return OPEN_CFW_PT_HANDLER_FAILED;
    if (mode == 1 && providers->set_display_parameters != NULL)
        result = providers->set_display_parameters(
            r[6], r[8], r[4] != 0U, providers->context) == 0 ? 0U : 1U;
    return open_cfw_pt_make_status_payload(0x38U, result, 3U, p, l);
}

static int open_cfw_pt_display_2e(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_display_providers *providers = c;
    int mode;
    uint8_t result = 5U;
    if (!open_cfw_pt_display_valid(r, n, 6U) || p == NULL || l == NULL)
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    mode = open_cfw_pt_display_mode(providers);
    if (mode < 0) return OPEN_CFW_PT_HANDLER_FAILED;
    if (mode == 1 && providers->set_runtime_flag != NULL)
        result = providers->set_runtime_flag(
            r[5] != 0U, providers->context) == 0 ? 0U : 1U;
    p[0]=0x3AU; p[1]=1U; p[2]=3U; p[3]=1U; p[4]=result; p[5]=r[4];
    *l=6U;
    return OPEN_CFW_PT_OK;
}

static int open_cfw_pt_display_3e(
    const uint8_t *r, uint8_t n, uint8_t *p, uint8_t *l, void *c)
{
    const struct open_cfw_pt_display_providers *providers = c;
    uint8_t current;
    uint8_t result;
    int mode;
    if (!open_cfw_pt_display_valid(r,n,5U) || p==NULL || l==NULL)
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    p[0]=0x3EU; p[1]=1U; p[2]=2U; p[3]=1U;
    mode=open_cfw_pt_display_mode(providers);
    if (mode < 0) return OPEN_CFW_PT_HANDLER_FAILED;
    if (mode != 1) result=5U;
    else if (r[4] > 1U) result=3U;
    else if (providers->get_aging_mode==NULL || providers->set_aging_mode==NULL ||
        providers->get_aging_mode(&current,providers->context)!=0)
        return OPEN_CFW_PT_HANDLER_FAILED;
    else if (current == r[4]) {
        p[4]=0U; p[5]=4U; *l=6U; return OPEN_CFW_PT_OK;
    } else result=providers->set_aging_mode(
        r[4]!=0U,providers->context)==0 ? 0U : 1U;
    p[4]=result; *l=5U;
    return OPEN_CFW_PT_OK;
}

int open_cfw_pt_bind_display_handlers(
    struct open_cfw_pt_protocol *protocol,
    const struct open_cfw_pt_display_providers *providers)
{
    static const struct { uint8_t command; open_cfw_pt_handler_fn handler; }
        bindings[]={
            {0x20U,open_cfw_pt_display_20},{0x22U,open_cfw_pt_display_22},
            {0x2DU,open_cfw_pt_display_2d},{0x2EU,open_cfw_pt_display_2e},
            {0x3EU,open_cfw_pt_display_3e},{0x6EU,open_cfw_pt_display_6e},
            {0x74U,open_cfw_pt_display_74},{0x75U,open_cfw_pt_display_75},
            {0x77U,open_cfw_pt_display_77},
        };
    size_t i;
    if(protocol==NULL||providers==NULL)return OPEN_CFW_PT_INVALID_ARGUMENT;
    for(i=0U;i<sizeof(bindings)/sizeof(bindings[0]);++i)
        if(open_cfw_pt_protocol_bind(protocol,bindings[i].command,
            bindings[i].handler,(void *)providers)!=0)return OPEN_CFW_PT_HANDLER_FAILED;
    return OPEN_CFW_PT_OK;
}
