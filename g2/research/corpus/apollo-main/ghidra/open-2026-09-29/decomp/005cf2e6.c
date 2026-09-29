
undefined4
PdtDistortionTest_common_data_handler
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = param_3;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_1 = 0x26;
    param_2 = DAT_005cf608;
    uVar2 = param_3;
    FUN_0043d574(3,DAT_005cf614,DAT_005cf610,DAT_005cf60c,0x26,DAT_005cf608,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,DAT_005cf618,DAT_005cf618,param_3,param_1,param_2,uVar2);
  }
  return 0;
}

