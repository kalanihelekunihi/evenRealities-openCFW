
undefined8
service_ancc_init(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_00497938;
  if (*DAT_00497938 == 0) {
    iVar2 = osMutexNew(0);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 99;
        param_3 = DAT_0049793c;
        FUN_0043d574(1,DAT_00497948,DAT_00497944,DAT_00497940,99,DAT_0049793c,param_4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0049794c,DAT_0049794c);
      }
      goto LAB_0049739c;
    }
  }
  iVar2 = osMutexAcquire(*piVar1,1000);
  if (iVar2 == 0) {
    FUN_0043c0e4(DAT_00497958,0x1e28,0);
    *DAT_0049795c = 0;
    *DAT_00497d24 = 0;
    osMutexRelease(*piVar1);
    CB_ANCC_InitMsgCountCallbacks();
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x6a;
      param_3 = DAT_00497950;
      FUN_0043d574(1,DAT_00497948,DAT_00497944,DAT_00497940,0x6a,DAT_00497950,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00497954);
    }
  }
LAB_0049739c:
  return CONCAT44(param_3,param_2);
}

