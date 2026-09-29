
void _thread_msg_handler(void)

{
  int iVar1;
  int iVar2;
  char local_114 [4];
  undefined1 *local_110;
  undefined1 auStack_10c [4];
  char local_108;
  char local_104;
  
  local_110 = (undefined1 *)0x0;
  while( true ) {
    iVar1 = DAT_00538b5c;
    iVar2 = osMessageQueueGet(*(undefined4 *)(DAT_00538b5c + 0xc),&local_110,0,0);
    if (iVar2 != 0) {
      return;
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00538b54,DAT_00538b50,PTR_s__thread_msg_handler_00538b6c,0xbc,
                   PTR_s_ble_production_task_msg_handler_p_00538b74);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__task_ble_production_ble_product_00538b78);
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00538b54,DAT_00538b50,PTR_s__thread_msg_handler_00538b6c,0xbd,
                   PTR_s_p_msg____p_00538b7c,local_110);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__task_ble_production_p_msg____p_00538b80,
                          PTR_s__task_ble_production_p_msg____p_00538b80,local_110);
    }
    if (local_110 == (undefined1 *)0x0) break;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00538b54,DAT_00538b50,PTR_s__thread_msg_handler_00538b6c,0xc1,
                   PTR_s_p_msg____s_00538b84,local_110);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__task_ble_production_p_msg____s_00538b88,
                          PTR_s__task_ble_production_p_msg____s_00538b88,local_110);
    }
    iVar2 = FUN_0044b610(local_110,&DAT_00538808,2);
    if (iVar2 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00538b54,DAT_00538b50,PTR_s__thread_msg_handler_00538b6c,0xc3,
                     PTR_s_AT_cmd_00538b68);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__task_ble_production_AT_cmd_00538b70,
                            PTR_s__task_ble_production_AT_cmd_00538b70);
      }
      AT_Handler(local_110);
      osMemoryPoolFree(*(undefined4 *)(iVar1 + 0x18),local_110);
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00538b54,DAT_00538b50,PTR_s__thread_msg_handler_00538b6c,200,
                     PTR_s_p_msg_>head_flag_1___0x_02X_00538b8c,*local_110);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__task_ble_production_p_msg_>head_00538b90,
                            PTR_s__task_ble_production_p_msg_>head_00538b90,*local_110);
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00538b54,DAT_00538b50,PTR_s__thread_msg_handler_00538b6c,0xc9,
                     PTR_s_p_msg_>head_flag_2___0x_02X_00538b94,local_110[1]);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__task_ble_production_p_msg_>head_00538b98,
                            PTR_s__task_ble_production_p_msg_>head_00538b98,local_110[1]);
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00538b54,DAT_00538b50,PTR_s__thread_msg_handler_00538b6c,0xca,
                     PTR_s_p_msg_>head_flag_3___0x_02X_00538b9c,local_110[2]);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__task_ble_production_p_msg_>head_00538ba0,
                            PTR_s__task_ble_production_p_msg_>head_00538ba0,local_110[2]);
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00538b54,DAT_00538b50,PTR_s__thread_msg_handler_00538b6c,0xcb,
                     PTR_s_p_msg_>head_pay_load_len____d_00538ba4,local_110[3]);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__task_ble_production_p_msg_>head_00538ba8,
                            PTR_s__task_ble_production_p_msg_>head_00538ba8,local_110[3]);
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00538b54,DAT_00538b50,PTR_s__thread_msg_handler_00538b6c,0xcc,
                     PTR_s_p_msg_>msg_buf_content__00538bac);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__task_ble_production_p_msg_>msg__00538bb0,
                            PTR_s__task_ble_production_p_msg_>msg__00538bb0);
      }
      FUN_0043dacc(PTR_s_production_00538bb4,0x10,local_110 + 4,local_110[3]);
      local_114[0] = '\0';
      FUN_0043c0e4(auStack_10c,0x100,0);
      iVar2 = _thread_ble_production_msg_head_check(local_110);
      if ((iVar2 != 0) && (iVar2 = _thread_ble_production_msg_crc_check(local_110), iVar2 != 0)) {
        pt_protocol_dispatch(local_110 + 4,local_110[3],auStack_10c,local_114);
        if ((local_114[0] != '\0') &&
           ((APP_BleNusSendDataMsg(auStack_10c,local_114[0]), local_108 == '\v' ||
            ((local_108 == '\x01' && (local_104 == '\0')))))) {
          osDelay(1000);
          FUN_0044b0ae();
        }
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00538b54,DAT_00538b50,PTR_s__thread_msg_handler_00538b6c,0xe2,
                       PTR_s_send_data_len____d_00538bb8,local_114[0]);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__task_ble_production_send_data_l_00538bbc,
                              PTR_s__task_ble_production_send_data_l_00538bbc,local_114[0]);
        }
      }
      osMemoryPoolFree(*(undefined4 *)(iVar1 + 0x18),local_110);
      local_110 = (undefined1 *)0x0;
    }
  }
  return;
}

