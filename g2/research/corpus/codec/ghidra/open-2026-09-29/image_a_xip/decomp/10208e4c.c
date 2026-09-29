
undefined4 gx8002_sample_app_init(void)

{
  int iVar1;
  undefined *puVar2;
  undefined *puVar3;
  
  puVar3 = PTR_s__YW_APP___s__d_10208e7c;
  puVar2 = PTR_s_SampleAppInit_10208e78;
  iVar1 = iRam10208e74;
  if (*(int *)(iRam10208e74 + 0x10) == 0) {
    *(undefined4 *)(iRam10208e74 + 0x10) = 1;
    gx8002_printf(puVar3,puVar2,0x15d);
    gx8002_notification_setup();
    gx8002_power_lock_create(iVar1 + 8);
  }
  return 0;
}

