
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 SVC_Settings_Init(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_0046bee8;
  FUN_0043c0e4(DAT_0046bee8,0x50,0);
  iVar2 = DAT_0046c694;
  FUN_00439be4(iVar1,*(undefined4 *)(DAT_0046c694 + 4),0x1c);
  FUN_00439be4(iVar1 + 0x1c,*(undefined4 *)(iVar2 + 0x18),4);
  FUN_00439be4(iVar1 + 0x20,*(undefined4 *)(iVar2 + 0x1c),0xc);
  als_function_37(*(undefined4 *)(iVar1 + 0x24));
  SVC_Settings_DumpSettingConfig();
  CB_CHG_RegisterBatInfoCallback(_DAT_0046c698);
  settings_apply_display_levels();
  settings_send_config_to_peer();
  return 0;
}

