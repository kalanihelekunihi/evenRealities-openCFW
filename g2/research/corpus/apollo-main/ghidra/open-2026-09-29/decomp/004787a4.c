
undefined8 FUN_004787a4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  ushort *puVar2;
  undefined4 uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  
  FUN_00475014(0,1);
  uVar3 = DAT_0047896c;
  puVar2 = DAT_00478968;
  FUN_0043c0e4(DAT_0047896c,*DAT_00478968,0);
  uVar4 = FUN_00473940();
  iVar5 = FUN_004d0a2c(DAT_00478974,uVar3,DAT_00478970,*puVar2 >> 2,param_1,param_2,param_3,param_4)
  ;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar4 & 1) == 1);
  }
  if (iVar5 == 0) {
    iVar5 = FUN_0043d0ce(uVar4);
    if (iVar5 << 0x1e < 0) {
      param_1 = 0x90;
      param_2 = DAT_0047898c;
      FUN_0043d574(4,DAT_00478984,DAT_00478980,DAT_0047897c,0x90,DAT_0047898c,0);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004793ec,DAT_004793ec,0);
    }
  }
  else {
    iVar6 = FUN_0043d0ce(uVar4);
    if (iVar6 << 0x1e < 0) {
      param_1 = 0x8e;
      param_2 = DAT_00478978;
      FUN_0043d574(1,DAT_00478984,DAT_00478980,DAT_0047897c,0x8e,DAT_00478978,iVar5);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00478988,DAT_00478988,iVar5);
    }
  }
  return CONCAT44(param_2,param_1);
}

