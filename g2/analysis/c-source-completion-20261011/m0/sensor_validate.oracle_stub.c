#include <stdint.h>
const uint16_t case_boot_sensor_prescale_table[12]={1,2,4,6,8,10,12,16,32,64,128,256};
uint32_t case_boot_sensor_clock_5474(void){return 0;}
uint32_t case_boot_sensor_clock_549c(void){return 0;}
uint32_t case_policy_sensor_divide(uint32_t a,uint32_t b){uint32_t q=0;for(uint32_t i=32;;--i){uint32_t x=i==32?0:a>>i;if(x>=b){a-=i==32?0:b<<i;q+=i==32?0:1u<<i;}if(i==0)break;}return q;}
