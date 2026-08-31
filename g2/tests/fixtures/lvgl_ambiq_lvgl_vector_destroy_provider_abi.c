/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_vector_destroy_provider.h"

void open_cfw_lvgl_vector_destroy_probe(lv_ll_t * list,
                                        vector_draw_task_cb callback,
                                        void * data)
{
    lv_vector_for_each_destroy_tasks(list, callback, data);
}
