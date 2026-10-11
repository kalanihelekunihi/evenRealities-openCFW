#include <stdint.h>
const uint8_t case_boot_sensor_divisor_table[8]={1,1,1,3,7,1,0,0};
const uint8_t case_boot_sensor_rate_table[8]={8,4,2,4,8,1,1,1};
uint32_t case_policy_sensor_divide(uint32_t a,uint32_t b){uint32_t q=0;for(uint32_t i=32;;--i){uint32_t x=i==32?0:a>>i;if(x>=b){a-=i==32?0:b<<i;q+=i==32?0:1u<<i;}if(i==0)break;}return q;}
