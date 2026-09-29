
undefined8 uled_mspi_init(void)

{
  char *pcVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 unaff_r5;
  
  pcVar1 = (char *)FUN_0050938e(1);
  uled_driver_identify(*pcVar1 == '\x06');
  if (*DAT_004ca664 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x90;
      FUN_0043d574(1,DAT_004ca674,DAT_004ca670,DAT_004ca6a8,0x90,DAT_004ca668);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ca678,DAT_004ca678);
    }
    uVar3 = 0xffffffff;
  }
  else {
    uVar3 = (**(code **)(*DAT_004ca664 + 8))(0x4ca2ad,*DAT_004ca6b0,DAT_004ca6ac);
  }
  return CONCAT44(unaff_r5,uVar3);
}

