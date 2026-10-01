#include "angle_model.h"
#include <assert.h>
#include <math.h>
int main(void){
 int16_t l[800]={0},r[800]={0};G2AngleResult a=g2_angle_model(l,r,800,10,0,0);
 assert(fabs(a.angle_rad+acos(-1.)/2)<1e-12 && a.quality==0);
 l[400]=1000;r[403]=1000;a=g2_angle_model(l,r,800,10,0,0);
 assert(fabs(a.delay_s-3./16000)<1e-12 && (int)(a.angle_rad*180/acos(-1.))==27);
 a=g2_angle_model(l,r,800,10,100,0);assert(isnan(a.angle_rad));
 return 0;
}
