
undefined8 watchdog_enable(void)

{
  undefined *puVar1;
  int iVar2;
  char *pcVar3;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  iVar2 = FUN_0043d0ce();
  puVar1 = PTR_s_watchdog_enable_0052f380;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x15;
    FUN_0043d574(3,PTR_s_watchdog_0052f378,PTR_s_D__01_workspace_s200_ap510b_iar__0052f374,
                 PTR_s_watchdog_enable_0052f384);
    unaff_r6 = puVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__watchdog_watchdog_enable_0052f388,
                        PTR_s__watchdog_watchdog_enable_0052f388);
  }
  pcVar3 = (char *)FUN_0050938e(0);
  if (*pcVar3 == '\x01') {
    FUN_00511882();
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

