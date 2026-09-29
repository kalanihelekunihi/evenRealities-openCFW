
undefined4 SVC_KvdbReadDashboardAutoCloseValue(void)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 in_r3;
  undefined4 local_c;
  
  local_c = in_r3;
  iVar2 = FUN_0045a570();
  if (iVar2 != 2) {
    FUN_0043c0e4(&local_c,4,0);
    iVar2 = SVC_KvdbBlobRead(DAT_00492c0c,&local_c,4);
    puVar1 = DAT_00492c10;
    if (iVar2 < 1) {
      *DAT_00492c10 = 10;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00492bf8,DAT_00492bf4,PTR_s__kvdbUpdataDashboardAutoCloseVal_00492c18,
                     0x4c,PTR_s_kv_get_value_failed__SVC_KvdbRea_00492c20,*puVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__kv_module_cfg_kv_get_value_fail_00492c24,
                            PTR_s__kv_module_cfg_kv_get_value_fail_00492c24,*puVar1);
      }
    }
    else {
      *DAT_00492c10 = local_c;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00492bf8,DAT_00492bf4,PTR_s__kvdbUpdataDashboardAutoCloseVal_00492c18,
                     0x48,PTR_s_SVC_KvdbReadDashboardAutoCloseVa_00492c14,*puVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__kv_module_cfg_SVC_KvdbReadDashb_00492c1c,
                            PTR_s__kv_module_cfg_SVC_KvdbReadDashb_00492c1c,*puVar1);
      }
    }
  }
  return 0;
}

