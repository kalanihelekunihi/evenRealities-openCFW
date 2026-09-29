
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 quicklist_data_mutex_init(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  piVar1 = DAT_004ffba8;
  if (*DAT_004ffba8 == 0) {
    iVar2 = osMutexNew(0);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_3 = 0x23;
        FUN_0043d574(1,DAT_004ffbb8,DAT_004ffbb4,_DAT_004ffbb0,0x23,_DAT_004ffbac);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,_DAT_004ffbbc,_DAT_004ffbbc);
      }
      uVar3 = 8;
      goto LAB_004ffac6;
    }
  }
  uVar3 = 0;
LAB_004ffac6:
  return CONCAT44(param_3,uVar3);
}

