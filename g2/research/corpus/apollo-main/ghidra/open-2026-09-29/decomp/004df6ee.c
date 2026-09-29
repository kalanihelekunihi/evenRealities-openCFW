
undefined8 FUN_004df6ee(int *param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined *local_c;
  
  local_10 = param_3;
  local_c = param_4;
  if (param_1 == (int *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_c = DAT_004dffd8;
      local_10 = 0x129;
      FUN_0043d574(2,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,DAT_004dffdc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004dffe0,DAT_004dffe0);
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_c = DAT_004dffe4;
      local_10 = 0x12d;
      FUN_0043d574(4,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,DAT_004dffdc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004dffe8);
    }
    if (*param_1 != 0) {
      FUN_0044d7b8(*param_1);
      *param_1 = 0;
    }
    if (param_1[6] != 0) {
      ui_common_api_fn_00509f52(param_1[6]);
      ui_common_api_fn_00509c96(param_1[6]);
      param_1[6] = 0;
    }
    file_heap_free(param_1);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_c = PTR_s_common_text_destroy__text_destro_004dffec;
      local_10 = 0x13f;
      FUN_0043d574(3,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,DAT_004dffdc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__common_text_container_common_te_004e0288,
                          PTR_s__common_text_container_common_te_004e0288);
    }
  }
  return CONCAT44(local_c,local_10);
}

