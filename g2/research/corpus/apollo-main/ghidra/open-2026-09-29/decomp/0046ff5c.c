
undefined8 FUN_0046ff5c(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r6;
  undefined4 uVar3;
  
  iVar2 = FUN_0047021c(0x66,0,0,0,0);
  if (iVar2 != 0) {
    iVar2 = FUN_0043d0ce();
    uVar3 = DAT_00470888;
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004700a8,DAT_004700a4,DAT_0047088c,0x2c4);
      unaff_r6 = uVar3;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00470890);
    }
  }
  FUN_004910f4(1);
  uVar3 = 0;
  iVar2 = FUN_0047021c(0x99,0,0,0);
  if (iVar2 != 0) {
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_00470898;
    if (iVar2 << 0x1e < 0) {
      uVar3 = 0x2c9;
      FUN_0043d574(1,DAT_004700a8,DAT_004700a4,DAT_0047088c);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004709b4);
    }
  }
  FUN_004910f4(0x32);
  return CONCAT44(unaff_r6,uVar3);
}

