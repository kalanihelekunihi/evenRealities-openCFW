
int TouchSetAppMeta(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined4 local_2c;
  undefined1 uStack_28;
  undefined3 local_27;
  undefined1 uStack_24;
  undefined3 uStack_23;
  undefined1 auStack_20 [16];
  undefined4 uStack_10;
  
  uVar1 = DAT_005608b8;
  local_2c = *DAT_005608e0;
  uStack_28 = (undefined1)DAT_005608e0[1];
  local_27 = (undefined3)param_1;
  uStack_23 = (undefined3)((uint)DAT_005608e0[2] >> 8);
  uStack_24 = (undefined1)((uint)param_1 >> 0x18);
  uStack_10 = param_4;
  iVar2 = semantic_TouchBuildAndSendFrame(DAT_005608b8,0x4c,&local_2c,9);
  if (iVar2 == 0) {
    iVar2 = semantic_TouchSendCommandRetry(uVar1,auStack_20,0xf);
    if (iVar2 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_005608c8,DAT_005608c4,DAT_005608e8,0x20f,DAT_005608f8);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_005608fc,DAT_005608fc);
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005608c8,DAT_005608c4,DAT_005608e8,0x20d,DAT_005608f0,iVar2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_005608f4,DAT_005608f4,iVar2);
      }
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005608c8,DAT_005608c4,DAT_005608e8,0x207,DAT_005608e4,iVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_005608ec,DAT_005608ec,iVar2);
    }
  }
  return iVar2;
}

