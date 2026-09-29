
undefined4 FUN_00558804(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 in_r3;
  
  uVar3 = DAT_00558920;
  iVar1 = file_remove(DAT_00558920);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005588bc,DAT_005588b8,DAT_0055893c,0x14f,DAT_00558944,uVar3);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_00558948,DAT_00558948,uVar3);
    }
    uVar3 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_005588bc,DAT_005588b8,DAT_0055893c,0x14c,DAT_00558938,uVar3,iVar1,in_r3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8800000,DAT_00558940,DAT_00558940,uVar3,iVar1);
    }
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

