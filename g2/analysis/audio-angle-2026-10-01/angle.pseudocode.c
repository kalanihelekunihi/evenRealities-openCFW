/* Manual readable reconstruction of0x5918cc and0x5918b0.
 * Finite normal inputs, bounded n/lag; not binary-equivalent firmware code.
 * Stock ABI: r0/r1=left/right,r2=n,r3=max_lag; d0=sample rate,d1=spacing,
 * d2=speed,d3=RMS floor,d4=quality floor; four output pointers on stack.
 */
#include "angle_model.h"
#include <math.h>
#include <limits.h>
G2AngleResult g2_angle_model(const int16_t *l,const int16_t *r,int n,
                            int lim,double rms_floor,double quality_floor) {
 G2AngleResult o={NAN,NAN,0,0};
 if(n<1)return o;
 int64_t el=0,er=0;
 for(int i=0;i<n;i++){el+=(int64_t)l[i]*l[i];er+=(int64_t)r[i]*r[i];}
 o.max_rms=fmax(sqrt((double)el/n),sqrt((double)er/n));
 if(o.max_rms<rms_floor)return o;
 if(lim<1)lim=8;
 int best_lag=0;int64_t best=INT64_MIN;double sum_abs=0;
 for(int lag=-lim;lag<=lim;lag++) {
  int64_t corr=0;
  if(lag<0){for(int i=0;i<n+lag;i++)corr+=(int64_t)r[i]*l[i-lag];}
  else {for(int i=0;i<n-lag;i++)corr+=(int64_t)r[i+lag]*l[i];}
  if(corr>best){best=corr;best_lag=lag;} /* strict >: first tie wins */
  sum_abs+=fabs((double)corr);
 }
 double mean_abs=sum_abs/(2*lim+1);
 o.quality=mean_abs>0?(double)best/(mean_abs+1e-12):0;
 if(o.quality<quality_floor)return o;
 o.delay_s=best_lag/G2_ANGLE_SAMPLE_RATE;
 double x=o.delay_s*G2_ANGLE_SPEED/G2_ANGLE_SPACING;
 if(x < -1)x=-1;
 if(x > 1)x=1;
 o.angle_rad=asin(x);
 return o;
}
/* Stock wrapper0x591ba4 uses n800,lim10,rms_floor0,quality_floor0;
 * returns (int16_t)trunc(angle_rad*180/pi), discarding quality/RMS/delay.
 * ABI-output pointer checks in general helper allow null output slots.
 */
