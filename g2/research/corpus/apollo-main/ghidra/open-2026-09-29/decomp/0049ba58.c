
undefined8
setting_respond_with_local_data_serialize
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uStack_10;
  
  uStack_10 = param_4;
  iVar1 = FUN_0045a568();
  uVar2 = DAT_0049bffc;
  if (iVar1 == 1) {
    uStack_10 = 0x100;
    if (*DAT_0049bbf0 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_2 = 0x14a;
        FUN_0043d574(1,DAT_0049bbc0,DAT_0049bbbc,PTR_s_setting_respond_with_local_data__0049c010,
                     0x14a,DAT_0049bff4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0049bff8);
      }
      uVar2 = 1;
    }
    else {
      FUN_0043c0e4(DAT_0049bffc,0x100,0);
      iVar1 = setting_respond_with_local_data(uVar2,&uStack_10);
      if (iVar1 == 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          param_2 = 0x153;
          FUN_0043d574(1,DAT_0049bbc0,DAT_0049bbbc,PTR_s_setting_respond_with_local_data__0049c010,
                       0x153,PTR_s_respond_local_data_failed_0049c014);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__pb_service_setting_respond_loca_0049c018,
                              PTR_s__pb_service_setting_respond_loca_0049c018);
        }
        uVar2 = 0x2b;
      }
      else {
        iVar1 = FUN_0045a568();
        if (iVar1 == 1) {
          Thread_MsgPbTxByBle(1,9,uVar2,uStack_10 & 0xffff,param_2,param_3);
        }
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          param_2 = 0x15a;
          FUN_0043d574(4,DAT_0049bbc0,DAT_0049bbbc,PTR_s_setting_respond_with_local_data__0049c010,
                       0x15a,PTR_s__Send_Local_Data__BLE_sent_succe_0049c01c);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__pb_service_setting__Send_Local_D_0049c020,
                              PTR_s__pb_service_setting__Send_Local_D_0049c020);
        }
        uVar2 = 0;
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x142;
      FUN_0043d574(4,DAT_0049bbc0,DAT_0049bbbc,PTR_s_setting_respond_with_local_data__0049c010,0x142
                   ,DAT_0049bfe8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0049bff0,DAT_0049bff0);
    }
    uVar2 = 0;
  }
  return CONCAT44(param_2,uVar2);
}

