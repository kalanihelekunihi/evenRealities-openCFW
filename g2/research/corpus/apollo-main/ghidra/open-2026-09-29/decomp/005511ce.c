
undefined8 FUN_005511ce(int param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  byte *pbVar1;
  int iVar2;
  
  pbVar1 = DAT_00551ab8;
  if (param_1 != 0) {
    if (*DAT_00551ab8 == 0) {
      *DAT_00551ab8 = 3;
      FUN_00551ed8(param_1,1);
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_3 = (uint)*pbVar1;
        param_1 = 0x581;
        param_2 = DAT_00551310;
        FUN_0043d574(2,DAT_005514b8,DAT_0055148c,DAT_00551e58,0x581,DAT_00551310,param_3,param_4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_00551318,DAT_00551318,*pbVar1,param_1,param_2,param_3);
      }
    }
  }
  return CONCAT44(param_2,param_1);
}

