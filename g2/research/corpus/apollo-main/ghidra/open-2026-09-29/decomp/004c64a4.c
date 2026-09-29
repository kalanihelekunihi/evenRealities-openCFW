
void device_mgr_fn_004c64a4(void)

{
  int iVar1;
  
  CHG_DeinitBatterySync();
  func_0x004ff8dc();
  FUN_004ac0f8();
  iVar1 = DAT_004c6c08;
  if (*(int *)(DAT_004c6c08 + 8) != 0) {
    osThreadTerminate(*(undefined4 *)(DAT_004c6c08 + 8));
    *(undefined4 *)(iVar1 + 8) = 0;
  }
  return;
}

