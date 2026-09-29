
uint FUN_00440968(uint param_1,uint param_2,uint param_3,int param_4)

{
  uint uVar1;
  
  if (((param_2 & 0x60000000) == 0x20000000) && ((int)(param_2 & 0x9fffffff) < 0x1fffffff)) {
    if ((int)(param_2 & 0x9fffffff) < 0x10000000) {
      param_2 = param_2 & 0x9fffffff;
    }
    else {
      param_2 = 0xfffffff - (param_2 & 0x9fffffff);
    }
    param_2 = (int)(param_2 * param_4) / 100;
  }
  if (((param_3 & 0x60000000) == 0x20000000) && ((int)(param_3 & 0x9fffffff) < 0x1fffffff)) {
    if ((int)(param_3 & 0x9fffffff) < 0x10000000) {
      param_3 = param_3 & 0x9fffffff;
    }
    else {
      param_3 = 0xfffffff - (param_3 & 0x9fffffff);
    }
    param_3 = (int)(param_3 * param_4) / 100;
  }
  uVar1 = param_3;
  if ((int)param_1 < (int)param_3) {
    uVar1 = param_1;
  }
  if (((int)param_2 <= (int)uVar1) && (param_2 = param_1, (int)param_3 <= (int)param_1)) {
    param_2 = param_3;
  }
  return param_2;
}

