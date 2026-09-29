
undefined4 gx8002_app_initialize(void)

{
  uint uVar1;
  undefined *puStack_14;
  undefined *puStack_10;
  undefined *puStack_c;
  undefined *puStack_8;
  
  LvpQueueInit(uRam10208d2c,uRam10208d28,0x40,8);
  if ((*piRam10208d30 != 0) && (uVar1 = *(uint *)(*piRam10208d30 + 4), uVar1 != 0)) {
    (*(code *)(uVar1 & 0xfffffffe))();
  }
  puStack_14 = PTR_gx8002_app_suspend_10208d34;
  puStack_10 = PTR_s__LvpAppSuspend_10208d38;
  puStack_c = PTR_gx8002_app_resume_10208d3c;
  puStack_8 = PTR_s__LvpAppResume_10208d40;
  gx8002_register_suspend(&puStack_14);
  gx8002_register_resume(&puStack_c);
  gx8002_watchdog_initialize(3000,2999,PTR_gx8002_watchdog_callback_10208d44,0);
  return 0;
}

