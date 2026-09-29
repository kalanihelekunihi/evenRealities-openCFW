
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 health_data_mutex_init(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  piVar1 = DAT_004ffdd0;
  if (*DAT_004ffdd0 == 0) {
    iVar2 = osMutexNew(0);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_3 = 0x28;
        FUN_0043d574(1,DAT_004ffde0,DAT_004ffddc,_DAT_004ffdd8,0x28,_DAT_004ffdd4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,_DAT_004ffde4,_DAT_004ffde4);
      }
      uVar3 = 0xffffffff;
      goto LAB_004ffc30;
    }
  }
  uVar3 = 0;
LAB_004ffc30:
  return CONCAT44(param_3,uVar3);
}

