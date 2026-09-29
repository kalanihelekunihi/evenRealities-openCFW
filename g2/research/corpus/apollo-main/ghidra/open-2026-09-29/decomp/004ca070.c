
undefined4 uled_safe_get_chip_id(void)

{
  int iVar1;
  undefined4 uVar2;
  
  if (*DAT_004ca664 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ca674,DAT_004ca670,DAT_004ca6bc,0xb1,DAT_004ca668);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ca678,DAT_004ca678);
    }
    uVar2 = 0xffff;
  }
  else {
    (**(code **)(*DAT_004ca664 + 4))(&stack0xfffffff4);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004ca674,DAT_004ca670,DAT_004ca6bc,0xb7,DAT_004ca6c0,0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004ca6c4,DAT_004ca6c4,0);
    }
    uVar2 = 0;
  }
  return uVar2;
}

