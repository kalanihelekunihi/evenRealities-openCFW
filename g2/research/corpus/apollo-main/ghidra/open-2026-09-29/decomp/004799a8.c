
void FUN_004799a8(int param_1,byte param_2)

{
  bool bVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  
  iVar6 = DAT_0047a2dc + (uint)param_2 * 0x100;
  FUN_00475014(0,1);
  uVar2 = DAT_0047a470;
  iVar3 = FUN_004d0a2c(DAT_0047a470,param_1,iVar6,0x20);
  uVar4 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar4 = getCurrentExceptionNumber();
    uVar4 = uVar4 & 0x1ff;
  }
  if (uVar4 == 0) {
    osThreadYield();
  }
  iVar6 = FUN_004d0a2c(uVar2,param_1 + 0x80,iVar6 + 0x80,0x20);
  if (iVar6 == 0 && iVar3 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_0047a478,0x1b3,DAT_0047a5bc,0x40,0x20,param_2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_0047a700,DAT_0047a700,0x40,0x20,param_2);
    }
  }
  else {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0047a2e4,DAT_0047a2e0,DAT_0047a478,0x1b0,DAT_0047a474,iVar3,iVar6);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_0047a5b8,DAT_0047a5b8,iVar3,iVar6);
    }
  }
  return;
}

