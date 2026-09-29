
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
terminal_action_mutex_init_internal(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  piVar1 = _DAT_005e4768;
  if (*_DAT_005e4768 == 0) {
    iVar2 = osMutexNew(PTR_DAT_005e476c);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_3 = 0x38;
        FUN_0043d574(1,DAT_005e477c,DAT_005e4778,PTR_s_terminal_action_mutex_init_inter_005e4774,
                     0x38,PTR_s_terminal_action_mutex_create_fai_005e4770);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,_DAT_005e4780,_DAT_005e4780);
      }
      uVar3 = 0xffffffff;
      goto LAB_005e438c;
    }
  }
  uVar3 = 0;
LAB_005e438c:
  return CONCAT44(param_3,uVar3);
}

