/* SPDX-License-Identifier: MIT */
#include "src/draw/lv_image_decoder.h"

lv_result_t open_cfw_lvgl_decoder_open_probe(lv_image_decoder_dsc_t * descriptor,
                                              const void * source,
                                              const lv_image_decoder_args_t * arguments)
{
    return lv_image_decoder_open(descriptor, source, arguments);
}

void open_cfw_lvgl_decoder_close_probe(lv_image_decoder_dsc_t * descriptor)
{
    lv_image_decoder_close(descriptor);
}
