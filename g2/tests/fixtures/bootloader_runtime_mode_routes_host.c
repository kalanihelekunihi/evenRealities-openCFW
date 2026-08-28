/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include "../../components/bootloader/core_overlay/runtime_mode_routes_4222f0.c"
uint8_t open_cfw_route_host_configuration[20], open_cfw_route_fixture_bitmap[7][64];
uint32_t open_cfw_route_fixture_enable_calls[7], open_cfw_route_fixture_disable_calls[7], open_cfw_route_fixture_last_bit, open_cfw_route_fixture_copy_calls;
uint32_t open_cfw_route_host_bitmap_test(uint32_t row,uint32_t bit){return row<7U&&bit<64U?open_cfw_route_fixture_bitmap[row][bit]:0U;}
uint32_t open_cfw_route_host_enable(uint8_t row,uint8_t bit){++open_cfw_route_fixture_enable_calls[row];open_cfw_route_fixture_last_bit=bit;open_cfw_route_fixture_bitmap[row][bit]=1U;return 0x10U+row;}
uint32_t open_cfw_route_host_disable(uint8_t row,uint8_t bit){++open_cfw_route_fixture_disable_calls[row];open_cfw_route_fixture_last_bit=bit;open_cfw_route_fixture_bitmap[row][bit]=0U;return 0x20U+row;}
void open_cfw_route_host_copy(void *d,const void *s,uint32_t n){uint32_t i;++open_cfw_route_fixture_copy_calls;for(i=0;i<n;++i)((uint8_t*)d)[i]=((const uint8_t*)s)[i];}
void open_cfw_route_fixture_reset(void){uint32_t i,j;for(i=0;i<7;++i){open_cfw_route_fixture_enable_calls[i]=0;open_cfw_route_fixture_disable_calls[i]=0;for(j=0;j<64;++j)open_cfw_route_fixture_bitmap[i][j]=0;}for(i=0;i<20;++i)open_cfw_route_host_configuration[i]=0;open_cfw_route_fixture_last_bit=0;open_cfw_route_fixture_copy_calls=0;}
