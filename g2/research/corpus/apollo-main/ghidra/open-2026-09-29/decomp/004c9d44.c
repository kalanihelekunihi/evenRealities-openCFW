
undefined8 uled_mspi_term(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  if (*DAT_004ca664 == 0) {
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_004ca668;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x4b;
      FUN_0043d574(1,DAT_004ca674,DAT_004ca670,DAT_004ca66c);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ca678,DAT_004ca678);
    }
  }
  else {
    (**(code **)*DAT_004ca664)();
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

