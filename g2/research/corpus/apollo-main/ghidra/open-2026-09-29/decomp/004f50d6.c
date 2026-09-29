
int FUN_004f50d6(int param_1,int param_2,undefined4 param_3,undefined4 param_4,int param_5,
                int param_6,int *param_7)

{
  int iVar1;
  undefined1 auStack_2c [4];
  int local_28;
  undefined4 uStack_24;
  
  if ((param_1 == 0) || (param_2 == 0)) {
    if (param_7 != (int *)0x0) {
      *param_7 = 0x1c;
    }
    iVar1 = 1;
  }
  else {
    uStack_24 = param_4;
    iVar1 = FUN_0044a43c(param_1);
    if (iVar1 == 0) {
      if (param_7 != (int *)0x0) {
        *param_7 = 0x1c;
      }
      iVar1 = 1;
    }
    else {
      FUN_0043c0e4(auStack_2c,8,0);
      FUN_00489546(auStack_2c,param_1,param_2,param_4,param_5,param_3,0);
      param_5 = param_5 + *(int *)(param_2 + 0xc);
      if (param_5 < 1) {
        param_5 = 0x1c;
      }
      iVar1 = (param_5 + local_28 + -1) / param_5;
      if (iVar1 < 1) {
        iVar1 = 1;
      }
      if ((0 < param_6) && (param_6 < iVar1)) {
        iVar1 = param_6;
      }
      if (param_7 != (int *)0x0) {
        *param_7 = param_5 * iVar1;
      }
    }
  }
  return iVar1;
}

