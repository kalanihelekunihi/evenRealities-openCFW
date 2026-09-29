
undefined8 uled_driver_power_up(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  if ((*DAT_004ca664 == 0) || (*(int *)(*DAT_004ca664 + 0x10) == 0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 200;
      FUN_0043d574(1,DAT_004ca674,DAT_004ca670,DAT_004ca6d0,200,DAT_004ca6cc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ca6d4,DAT_004ca6d4);
    }
    uVar2 = 0xffffffff;
  }
  else {
    uVar2 = (**(code **)(*DAT_004ca664 + 0x10))();
  }
  return CONCAT44(unaff_r5,uVar2);
}

