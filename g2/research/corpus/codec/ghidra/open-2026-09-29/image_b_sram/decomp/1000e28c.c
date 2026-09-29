
void FUN_1000e28c(short *param_1,int param_2,uint param_3)

{
  short *psVar1;
  
  if ((int)param_3 < 1) {
    if (0 < param_2) {
      psVar1 = param_1 + param_2;
      do {
        *param_1 = (short)((int)*param_1 << (-param_3 & 0x3f));
        param_1 = param_1 + 1;
      } while (param_1 != psVar1);
      return;
    }
  }
  else if (0 < param_2) {
    psVar1 = param_1 + param_2;
    do {
      *param_1 = (short)((int)*param_1 >> (param_3 & 0x3f));
      param_1 = param_1 + 1;
    } while (psVar1 != param_1);
  }
  return;
}

