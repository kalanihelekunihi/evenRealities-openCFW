
undefined8 watchdog_init(void)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  watchdog_enable();
  iVar2 = FUN_0043d0ce();
  puVar1 = PTR_s_watchdog_init_0052f36c;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0xe;
    FUN_0043d574(3,PTR_s_watchdog_0052f378,PTR_s_D__01_workspace_s200_ap510b_iar__0052f374,
                 PTR_s_watchdog_init_0052f370);
    unaff_r6 = puVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__watchdog_watchdog_init_0052f37c,
                        PTR_s__watchdog_watchdog_init_0052f37c);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

