
undefined8 FUN_004706e0(void)

{
  int iVar1;
  int iVar2;
  undefined4 in_r3;
  undefined4 uVar3;
  
  uVar3 = 0;
  iVar1 = FUN_0047021c(4,0,0,0,0,in_r3);
  if (iVar1 != 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar3 = 0x3fe;
      FUN_0043d574(2,DAT_00470a7c,DAT_00470a78,DAT_00470f5c,0x3fe,DAT_00470898);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004709b4);
    }
  }
  return CONCAT44(uVar3,iVar1);
}

