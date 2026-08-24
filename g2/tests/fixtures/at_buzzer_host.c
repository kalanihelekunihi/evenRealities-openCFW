#include "at_buzzer_host.h"
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

char open_cfw_test_at_buzzer_output[2048];
unsigned int open_cfw_test_at_buzzer_output_count;
unsigned int open_cfw_test_at_buzzer_note_count;
unsigned int open_cfw_test_at_buzzer_play_count;
unsigned int open_cfw_test_at_buzzer_start_count;
unsigned int open_cfw_test_at_buzzer_stop_count;
uint32_t open_cfw_test_at_buzzer_arguments[3];

void open_cfw_test_at_buzzer_reset(void)
{
    open_cfw_test_at_buzzer_output[0]='\0';open_cfw_test_at_buzzer_output_count=0;
    open_cfw_test_at_buzzer_note_count=0;open_cfw_test_at_buzzer_play_count=0;
    open_cfw_test_at_buzzer_start_count=0;open_cfw_test_at_buzzer_stop_count=0;
    memset(open_cfw_test_at_buzzer_arguments,0,sizeof(open_cfw_test_at_buzzer_arguments));
}
void open_cfw_test_at_buzzer_emit(const char *format,...)
{
    size_t used=strlen(open_cfw_test_at_buzzer_output);va_list args;
    va_start(args,format);(void)vsnprintf(open_cfw_test_at_buzzer_output+used,
        sizeof(open_cfw_test_at_buzzer_output)-used,format,args);va_end(args);
    ++open_cfw_test_at_buzzer_output_count;
}
void open_cfw_test_at_buzzer_note(uint8_t note,uint8_t tone,uint8_t beat)
{open_cfw_test_at_buzzer_arguments[0]=note;open_cfw_test_at_buzzer_arguments[1]=tone;open_cfw_test_at_buzzer_arguments[2]=beat;++open_cfw_test_at_buzzer_note_count;}
void open_cfw_test_at_buzzer_play(uint32_t type)
{open_cfw_test_at_buzzer_arguments[0]=type;++open_cfw_test_at_buzzer_play_count;}
void open_cfw_test_at_buzzer_start(uint32_t frequency,uint8_t duty)
{open_cfw_test_at_buzzer_arguments[0]=frequency;open_cfw_test_at_buzzer_arguments[1]=duty;++open_cfw_test_at_buzzer_start_count;}
void open_cfw_test_at_buzzer_stop(void){++open_cfw_test_at_buzzer_stop_count;}
