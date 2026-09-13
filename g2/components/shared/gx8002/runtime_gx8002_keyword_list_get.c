/* SPDX-License-Identifier: MIT */
#include <lvp_param.h>
extern LVP_KWS_PARAM_LIST open_cfw_gx8002_max_keyword_list;
LVP_KWS_PARAM_LIST *open_cfw_gx8002_keyword_list_get(void)
{
    return &open_cfw_gx8002_max_keyword_list;
}
