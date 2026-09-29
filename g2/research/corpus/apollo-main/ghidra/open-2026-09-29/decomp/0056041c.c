
int TouchExitDFU(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar1 = semantic_TouchBuildAndSendFrame(DAT_005608b8,0x3b,0,0,param_1,param_2,param_3,param_4);
  if (iVar1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005608c8,DAT_005608c4,DAT_00560ef0,0x25f,DAT_00560ef8);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0056107c,DAT_0056107c);
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005608c8,DAT_005608c4,DAT_00560ef0,0x25d,DAT_00560eec,iVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00560ef4,DAT_00560ef4,iVar1);
    }
  }
  return iVar1;
}

