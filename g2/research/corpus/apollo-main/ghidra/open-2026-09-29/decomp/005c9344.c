
float FUN_005c9344(float param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  uint in_fpscr;
  int iVar3;
  
  if ((((int)param_1 & 0x60000000U) == 0x20000000) &&
     ((int)((int)param_1 & 0x9fffffffU) < 0x1fffffff)) {
    if ((int)((int)param_1 & 0x9fffffffU) < 0x10000000) {
      uVar1 = (int)param_1 & 0x9fffffff;
    }
    else {
      uVar1 = 0xfffffff - ((int)param_1 & 0x9fffffffU);
    }
    iVar2 = param_2;
    if ((int)(uVar1 * param_2) / 100 < param_2) {
      if ((int)((int)param_1 & 0x9fffffffU) < 0x10000000) {
        uVar1 = (int)param_1 & 0x9fffffff;
      }
      else {
        uVar1 = 0xfffffff - ((int)param_1 & 0x9fffffffU);
      }
      iVar2 = (int)(uVar1 * param_2) / 100;
    }
    iVar3 = DAT_005c9718;
    if (-1 < iVar2) {
      if ((int)((int)param_1 & 0x9fffffffU) < 0x10000000) {
        uVar1 = (int)param_1 & 0x9fffffff;
      }
      else {
        uVar1 = 0xfffffff - ((int)param_1 & 0x9fffffffU);
      }
      iVar3 = param_2;
      if ((int)(uVar1 * param_2) / 100 < param_2) {
        if ((int)((int)param_1 & 0x9fffffffU) < 0x10000000) {
          uVar1 = (int)param_1 & 0x9fffffff;
        }
        else {
          uVar1 = 0xfffffff - ((int)param_1 & 0x9fffffffU);
        }
        iVar3 = (int)(uVar1 * param_2) / 100;
      }
    }
    param_1 = (float)VectorSignedToFloat(iVar3,(byte)(in_fpscr >> 0x16) & 3);
  }
  return param_1;
}

