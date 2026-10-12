#include <stdint.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
volatile uint32_t gx8002_image_b_gsensor_workstate_20016f60;
extern uint32_t gx8002_image_b_gsensor_workstate_100089e8(void);
static int calls;static uint32_t logged;
int gx8002_image_b_heap_log_10009934(const char *fmt,...){assert(strcmp(fmt,"gsensor_workstate =%d\n")==0);va_list ap;va_start(ap,fmt);logged=va_arg(ap,uint32_t);va_end(ap);calls++;gx8002_image_b_gsensor_workstate_20016f60=42;return 0;}
int main(void){gx8002_image_b_gsensor_workstate_20016f60=7;assert(gx8002_image_b_gsensor_workstate_100089e8()==42);assert(calls==1&&logged==7);puts("1/1 native two-read workstate fixture");return 0;}
