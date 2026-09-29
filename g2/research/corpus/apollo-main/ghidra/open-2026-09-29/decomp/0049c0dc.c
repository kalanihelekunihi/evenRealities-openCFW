
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_0049c0dc(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  
  iVar2 = FUN_00443484();
  if ((iVar2 == 1) && (iVar2 = FUN_004434d0(1), puVar1 = _DAT_0049cb1c, iVar2 == 1)) {
    *_DAT_0049cb20 = *_DAT_0049cb1c;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0x7e;
      param_2 = _DAT_0049cb24;
      FUN_0043d574(4,PTR_s_dashboard_0049cb30,DAT_0049cb2c,_DAT_0049cb28,0x7e,_DAT_0049cb24,*puVar1,
                   param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__dashboard_dashboard_reset_auto_c_0049cd10,
                          PTR_s__dashboard_dashboard_reset_auto_c_0049cd10,*puVar1);
    }
  }
  return CONCAT44(param_2,param_1);
}

