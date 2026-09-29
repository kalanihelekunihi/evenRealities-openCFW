
undefined8 slave_disconnect_restart_adv_work_0046f098(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar2 = FUN_0043d0ce();
  uVar1 = DAT_0046f454;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x2f9;
    FUN_0043d574(2,DAT_0046f404,DAT_0046f400,DAT_0046f458);
    unaff_r6 = uVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x8000000,DAT_0046f45c,DAT_0046f45c);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

