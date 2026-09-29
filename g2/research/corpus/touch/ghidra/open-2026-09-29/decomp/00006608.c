
undefined4 touch_sub_3308(int param_1,uint param_2,int *param_3)

{
  uint uVar1;
  
  if (param_2 - 2 < 2) {
    uVar1 = 0x1000000;
    param_2 = (param_2 & 1) << 0x18;
  }
  else {
    uVar1 = 1;
  }
  while( true ) {
    if ((*(uint *)(**(int **)(*param_3 + 8) + 0x180) & uVar1) != param_2) {
      return 0;
    }
    if (param_1 == 0) break;
    Cy_SysLib_DelayUs(1);
    param_1 = param_1 + -1;
  }
  return 4;
}

