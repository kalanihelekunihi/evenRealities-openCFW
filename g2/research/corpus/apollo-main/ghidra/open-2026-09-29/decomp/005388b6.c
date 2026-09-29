
undefined8
_thread_ble_production_msg_head_check(char *param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  byte bVar2;
  
  bVar2 = 0;
  if (((*param_1 == 'Z') && (param_1[1] == -0x5b)) && (param_1[2] == '\x7f')) {
    bVar2 = 1;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = 0x114;
      FUN_0043d574(1,DAT_00538b54,DAT_00538b50,PTR_s__thread_ble_production_msg_head__00538be4,0x114
                   ,PTR_s_ble_production_msg_head_check_fa_00538be0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__task_ble_production_ble_product_00538be8,
                          PTR_s__task_ble_production_ble_product_00538be8);
    }
  }
  return CONCAT44(param_3,(uint)bVar2);
}

