
undefined4
Quicklist_common_data_handler(int param_1,undefined4 param_2,undefined2 param_3,undefined4 param_4)

{
  int iVar1;
  
  quicklist_data_mutex_init();
  if (param_1 == 0) {
    iVar1 = APP_PbRxQuicklistFrameDataProcess(param_2,param_3);
    if ((iVar1 == 0) && (iVar1 = APP_DecodePbRxQuicklistData(), iVar1 == 0)) {
      FUN_004f5e84();
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004ffbb8,DAT_004ffbb4,PTR_s_Quicklist_common_data_handler_004ffbd0,0x69,
                   PTR_s_Unknown_event_type___d_004ffbcc,param_1,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__quicklist_page_Unknown_event_ty_004ffbd4,
                          PTR_s__quicklist_page_Unknown_event_ty_004ffbd4,param_1);
    }
  }
  return 0;
}

