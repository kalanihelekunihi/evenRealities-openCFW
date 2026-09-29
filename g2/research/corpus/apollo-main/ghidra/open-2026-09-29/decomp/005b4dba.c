
undefined4 FUN_005b4dba(int param_1,int param_2)

{
  int iVar1;
  
  if (param_2 != 0) {
    if (*(char *)(param_2 + 1) != '\0') {
      FUN_00439be4(param_1 + 1,param_2 + 2,5);
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,DAT_005b52d8,DAT_005b52d4,PTR_s_conversate_action_app_config_005b5660,0xd8,
                     DAT_005b55ac,*(undefined1 *)(param_1 + 1),*(undefined1 *)(param_1 + 2),
                     *(undefined1 *)(param_1 + 3),*(undefined1 *)(param_1 + 4),
                     *(undefined1 *)(param_1 + 5));
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xd400000,DAT_005b55b0,DAT_005b55b0,*(undefined1 *)(param_1 + 1),
                            *(undefined1 *)(param_1 + 2),*(undefined1 *)(param_1 + 3),
                            *(undefined1 *)(param_1 + 4),*(undefined1 *)(param_1 + 5));
      }
      FUN_005b133c();
    }
    FUN_005b02e4(0x10,0);
    return 0;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(1,DAT_005b52d8,DAT_005b52d4,PTR_s_conversate_action_app_config_005b5660,0xd1,
                 DAT_005b5418);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x4000000,DAT_005b5420);
  }
  return 0xffffffff;
}

