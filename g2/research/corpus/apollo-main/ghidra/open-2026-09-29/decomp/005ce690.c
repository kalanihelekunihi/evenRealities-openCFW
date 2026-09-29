
undefined4
RingDataRelay_common_data_handler(uint param_1,undefined4 param_2,uint param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar2 = param_2;
  uVar3 = param_3;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar2 = DAT_005ce7b0;
    uVar3 = param_1;
    param_4 = param_3;
    FUN_0043d574(4,DAT_005ce73c,DAT_005ce738,DAT_005ce7b4,0x105,DAT_005ce7b0,param_1,param_3);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_005ce6da;
  }
  compress_log_output(0x10800000,DAT_005ce7b8,DAT_005ce7b8,param_1,param_3,uVar2,uVar3,param_4);
LAB_005ce6da:
  if (param_1 == 0) {
    APP_PbRxRingFrameDataProcess(param_2,param_3 & 0xffff);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_005ce73c,DAT_005ce738,DAT_005ce7b4,0x113,DAT_005ce7bc,param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_005ce7c0,DAT_005ce7c0,param_1);
    }
  }
  return 0;
}

