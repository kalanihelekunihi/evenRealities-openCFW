
undefined8 tt_size_select(int *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = 0;
  param_1[0x1d] = param_2;
  if ((int)((uint)*(byte *)(*param_1 + 8) << 0x1f) < 0) {
    FT_Select_Metrics(*param_1);
    tt_size_reset(param_1,0);
  }
  else {
    iVar1 = (**(code **)(*(int *)(*param_1 + 0x21c) + 0x6c))(*param_1,param_2,param_1 + 3);
    if (iVar1 != 0) {
      param_1[0x1d] = -1;
    }
  }
  return CONCAT44(param_4,iVar1);
}

