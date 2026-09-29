
void FUN_0053a0b6(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined1 uStack_514;
  undefined1 auStack_513 [3];
  undefined1 auStack_510 [256];
  undefined1 auStack_410 [1024];
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  if ((param_1 == 0) || (*(short *)(param_1 + 2) == 0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_box_uart_mgr_0053a3b0,PTR_s_D__01_workspace_s200_ap510b_iar__0053a3ac,
                   PTR_s_DEV_BoxRevcMsgProcess_0053a3d0,0x7c,PTR_s_box_rcv_msg_err_0053a3a4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__box_uart_mgr_box_rcv_msg_err_0053a3b4,
                          PTR_s__box_uart_mgr_box_rcv_msg_err_0053a3b4);
    }
  }
  else {
    auStack_513[0] = 0;
    uStack_514 = 0;
    FUN_0043c0e4(auStack_410,0x400,0);
    FUN_0043c0e4(auStack_510,0x100,0);
    iVar1 = func_0x0055e75a(2);
    if (iVar1 == 0) {
      iVar1 = FUN_0055e90c(2);
      if (iVar1 != 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_box_uart_mgr_0053a3b0,PTR_s_D__01_workspace_s200_ap510b_iar__0053a3ac
                       ,PTR_s_DEV_BoxRevcMsgProcess_0053a3d0,0x92,
                       PTR_s_uart_clear_buffer_failed___d_0053a3dc,iVar1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4400000,PTR_s__box_uart_mgr_uart_clear_buffer_f_0053a3e0,
                              PTR_s__box_uart_mgr_uart_clear_buffer_f_0053a3e0,iVar1);
        }
      }
      iVar1 = FUN_00539e92(param_1,auStack_410,&uStack_514);
      if (iVar1 == 0) {
        iVar1 = pt_protocol_dispatch(auStack_410,uStack_514,auStack_510,auStack_513);
        if (iVar1 == 0) {
          osDelay(2);
          iVar1 = FUN_0053a010(2,auStack_510,auStack_513[0]);
          if (iVar1 == 0) {
            iVar1 = func_0x0055e956(2);
            if (iVar1 != 0) {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                FUN_0043d574(1,PTR_s_box_uart_mgr_0053a3b0,
                             PTR_s_D__01_workspace_s200_ap510b_iar__0053a3ac,
                             PTR_s_DEV_BoxRevcMsgProcess_0053a3d0,0xb1,
                             PTR_s_uart_tx_flush_failed___d_0053a3fc,iVar1);
              }
              iVar2 = FUN_0043d0ce();
              if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
                compress_log_output(0x4400000,PTR_s__box_uart_mgr_uart_tx_flush_fail_0053a400,
                                    PTR_s__box_uart_mgr_uart_tx_flush_fail_0053a400,iVar1);
              }
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(1,PTR_s_box_uart_mgr_0053a3b0,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0053a3ac,
                           PTR_s_DEV_BoxRevcMsgProcess_0053a3d0,0xa9,
                           PTR_s_box_uart_send_err__d_0053a3f4,iVar1);
            }
            iVar2 = FUN_0043d0ce();
            if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
              compress_log_output(0x4400000,PTR_s__box_uart_mgr_box_uart_send_err__0053a3f8,
                                  PTR_s__box_uart_mgr_box_uart_send_err__0053a3f8,iVar1);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_box_uart_mgr_0053a3b0,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0053a3ac,
                         PTR_s_DEV_BoxRevcMsgProcess_0053a3d0,0x9f,
                         PTR_s_box_uart_pack_err__d_0053a3ec,iVar1);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x4400000,PTR_s__box_uart_mgr_box_uart_pack_err__0053a3f0,
                                PTR_s__box_uart_mgr_box_uart_pack_err__0053a3f0,iVar1);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_box_uart_mgr_0053a3b0,PTR_s_D__01_workspace_s200_ap510b_iar__0053a3ac
                       ,PTR_s_DEV_BoxRevcMsgProcess_0053a3d0,0x98,
                       PTR_s_box_uart_unpack_err__d_0053a3e4,iVar1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4400000,PTR_s__box_uart_mgr_box_uart_unpack_er_0053a3e8,
                              PTR_s__box_uart_mgr_box_uart_unpack_er_0053a3e8,iVar1);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_box_uart_mgr_0053a3b0,PTR_s_D__01_workspace_s200_ap510b_iar__0053a3ac,
                     PTR_s_DEV_BoxRevcMsgProcess_0053a3d0,0x8a,PTR_s_uart_stop_failed___d_0053a3d4,
                     iVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__box_uart_mgr_uart_stop_failed____0053a3d8,
                            PTR_s__box_uart_mgr_uart_stop_failed____0053a3d8,iVar1);
      }
    }
    iVar1 = FUN_0055e68e(2);
    if (iVar1 != 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_box_uart_mgr_0053a3b0,PTR_s_D__01_workspace_s200_ap510b_iar__0053a3ac,
                     PTR_s_DEV_BoxRevcMsgProcess_0053a3d0,0xba,PTR_s_uart_start_failed___d_0053a404,
                     iVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__box_uart_mgr_uart_start_failed__0053a408,
                            PTR_s__box_uart_mgr_uart_start_failed__0053a408,iVar1);
      }
    }
    if ((iVar1 == 0) &&
       (iVar1 = pt_production_mode_orchestrate(auStack_410,uStack_514,auStack_510,auStack_513[0]),
       iVar1 != 0)) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_box_uart_mgr_0053a3b0,PTR_s_D__01_workspace_s200_ap510b_iar__0053a3ac,
                     PTR_s_DEV_BoxRevcMsgProcess_0053a3d0,0xc3,PTR_s_pt_cmd_execute_err__d_0053a40c,
                     iVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__box_uart_mgr_pt_cmd_execute_err_0053a410,
                            PTR_s__box_uart_mgr_pt_cmd_execute_err_0053a410,iVar1);
      }
    }
  }
  return;
}

