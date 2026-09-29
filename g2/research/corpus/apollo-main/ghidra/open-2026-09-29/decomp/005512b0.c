
undefined8 FUN_005512b0(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  byte *pbVar1;
  int iVar2;
  
  pbVar1 = DAT_00551ab8;
  if (*DAT_00551ab8 == 0) {
    FUN_0055131c();
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = (uint)*pbVar1;
      param_1 = 0x598;
      param_2 = DAT_00551310;
      FUN_0043d574(2,DAT_005514b8,DAT_0055148c,DAT_00551eb0,0x598,DAT_00551310,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_00551318,DAT_00551318,*pbVar1,param_1,param_2,param_3);
    }
  }
  return CONCAT44(param_2,param_1);
}

