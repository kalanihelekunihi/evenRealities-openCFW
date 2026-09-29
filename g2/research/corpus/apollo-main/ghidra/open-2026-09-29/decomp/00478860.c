
void FUN_00478860(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  int *piVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int local_20 [4];
  undefined4 uStack_10;
  
  piVar2 = DAT_00478990;
  uStack_10 = param_4;
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00478984,DAT_00478980,DAT_00478998,0x98,DAT_00478994,*piVar2,param_1);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10800000,DAT_0047899c,DAT_0047899c,*piVar2,param_1);
  }
  FUN_0043dacc(DAT_004789a0,0x10,piVar2,0x20);
  if (param_1 != *piVar2) {
    FUN_00439c04(local_20,DAT_004789a4,0x10);
    local_20[0] = param_1;
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00478984,DAT_00478980,DAT_00478998,0x9f,DAT_004789a8,piVar2,param_1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_004789ac,DAT_004789ac,piVar2,param_1);
    }
    uVar4 = FUN_00473940();
    iVar3 = FUN_004d0a2c(DAT_00478974,local_20,piVar2,4);
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((uVar4 & 1) == 1);
    }
    if (iVar3 != 0) {
      iVar5 = FUN_0043d0ce(uVar4);
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00478984,DAT_00478980,DAT_00478998,0xa9,DAT_00478978,iVar3);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00478988,DAT_00478988,iVar3);
      }
    }
    return;
  }
  return;
}

