#include <stdint.h>
#include <stdio.h>
#include <string.h>
extern void gx8002_image_b_imcra_block_scale_1000e28c(int16_t *,int,int);
extern int gx8002_image_b_imcra_peak_shift_1000e2c4(const int16_t *,int);
int main(void){struct {int16_t s[5];int n;int expected;} cases[]={
{{0},1,-15},{{1},1,-14},{{-1},1,-14},{{32767},1,0},{{-32768},1,1},
{{1,-23,512,8,0},5,-5},{{0,0,0,0,16384},5,0}};
unsigned pass=0;for(unsigned i=0;i<sizeof(cases)/sizeof(*cases);i++)
 if(gx8002_image_b_imcra_peak_shift_1000e2c4(cases[i].s,cases[i].n)==cases[i].expected)pass++;
int16_t x[]={-8,-1,0,1,8,-32768};gx8002_image_b_imcra_block_scale_1000e28c(x,6,1);
int16_t y[]={-4,-1,0,0,4,-16384};if(memcmp(x,y,sizeof x)==0)pass++;
gx8002_image_b_imcra_block_scale_1000e28c(x,6,-2);
int16_t z[]={-16,-4,0,0,16,0};if(memcmp(x,z,sizeof x)==0)pass++;
printf("IMCRA native-branch host fixtures %u/9\n",pass);return pass!=9;}
