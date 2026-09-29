
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_0049c728(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  undefined4 *puVar1;
  undefined2 *puVar2;
  int iVar3;
  undefined4 uStack_18;
  undefined *puStack_14;
  
  iVar3 = FUN_0043d0ce();
  uStack_18 = param_3;
  puStack_14 = param_4;
  if (iVar3 << 0x1e < 0) {
    puStack_14 = PTR_s_dashboard_clear_calendar_ui_data_0049cd94;
    uStack_18 = 0x121;
    FUN_0043d574(4,PTR_s_dashboard_0049cb30,DAT_0049cb2c,
                 PTR_s_dashboard_clear_calendar_ui_data_0049cd98);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__dashboard_dashboard_clear_calen_0049cd9c,
                        PTR_s__dashboard_dashboard_clear_calen_0049cd9c);
  }
  puVar1 = _DAT_0049cb14;
  osMutexAcquire(*_DAT_0049cb14,0xffffffff);
  puVar2 = _DAT_0049cda0;
  *_DAT_0049cda0 = 0;
  FUN_0043c0e4(puVar2 + 2,0x1080,0);
  FUN_0043c0e4(_DAT_0049cda4,0x1080,0);
  FUN_0043c0e4(_DAT_0049cda8,0x1088,0);
  osMutexRelease(*puVar1);
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    puStack_14 = _DAT_0049cdac;
    uStack_18 = 0x131;
    FUN_0043d574(4,PTR_s_dashboard_0049cb30,DAT_0049cb2c,
                 PTR_s_dashboard_clear_calendar_ui_data_0049cd98);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10000000,_DAT_0049cdb0,_DAT_0049cdb0);
  }
  return CONCAT44(puStack_14,uStack_18);
}

