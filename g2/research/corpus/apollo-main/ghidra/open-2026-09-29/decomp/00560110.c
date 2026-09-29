
int TouchSendOnePacket(undefined4 param_1,ushort param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined1 auStack_20 [16];
  undefined4 uStack_10;
  
  uVar1 = DAT_005608b8;
  uStack_10 = param_4;
  if (param_2 < 0x21) {
    iVar2 = semantic_TouchBuildAndSendFrame(DAT_005608b8,0x37,param_1,param_2);
    if (iVar2 == 0) {
      iVar2 = semantic_TouchSendCommandRetry(uVar1,auStack_20,0xf);
      if (iVar2 != 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_005608c8,DAT_005608c4,DAT_00560904,0x228,DAT_00560914,iVar2);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_00560ed4,DAT_00560ed4,iVar2);
        }
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005608c8,DAT_005608c4,DAT_00560904,0x221,DAT_0056090c,iVar2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00560910,DAT_00560910,iVar2);
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005608c8,DAT_005608c4,DAT_00560904,0x21c,DAT_00560900,param_2,0x20);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_00560908,DAT_00560908,param_2,0x20);
    }
    iVar2 = 3;
  }
  return iVar2;
}

