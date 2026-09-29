
undefined4 FUN_00539e92(int param_1,undefined4 param_2,undefined1 *param_3)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  ushort uVar4;
  ushort uVar5;
  ushort uVar6;
  ushort uVar7;
  
  if ((param_1 == 0) || (*(short *)(param_1 + 2) == 0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_box_uart_mgr_0053a3b0,PTR_s_D__01_workspace_s200_ap510b_iar__0053a3ac,
                   PTR_s_comm_read_0053a3a8,0x1a,PTR_s_box_rcv_msg_err_0053a3a4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__box_uart_mgr_box_rcv_msg_err_0053a3b4,
                          PTR_s__box_uart_mgr_box_rcv_msg_err_0053a3b4);
    }
    uVar2 = 0xffffffff;
  }
  else {
    iVar1 = *(int *)(param_1 + 4);
    for (uVar5 = 0; uVar5 < *(ushort *)(param_1 + 2); uVar5 = uVar5 + 1) {
      if (*(char *)(iVar1 + (uint)uVar5) != '\0') {
        uVar6 = *(short *)(param_1 + 2) - uVar5;
        if (*(char *)(iVar1 + (uint)uVar5) == 'T') {
          FUN_00439be4(param_2,iVar1 + (uint)uVar5,uVar6);
          *param_3 = (char)uVar6;
        }
        else {
          uVar7 = uVar6 + 0x7d;
          for (uVar4 = 0; (int)(uint)uVar4 < (int)(uVar6 - 1); uVar4 = uVar4 + 1) {
            uVar7 = *(byte *)(iVar1 + (uint)uVar4 + (uint)uVar5) + uVar7;
          }
          if ((uVar7 & 0xff) != (ushort)*(byte *)((uint)uVar6 + (uint)uVar5 + iVar1 + -1)) {
            iVar3 = FUN_0043d0ce();
            if (iVar3 << 0x1e < 0) {
              FUN_0043d574(1,PTR_s_box_uart_mgr_0053a3b0,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0053a3ac,PTR_s_comm_read_0053a3a8,
                           0x40,PTR_s_crc_check_failed__data_len____d__0053a3b8,uVar6,uVar7 & 0xff,
                           *(undefined1 *)((uint)uVar6 + (uint)uVar5 + iVar1 + -1));
            }
            iVar3 = FUN_0043d0ce();
            if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
              compress_log_output(0x4c00000,PTR_s__box_uart_mgr_crc_check_failed__d_0053a3bc,
                                  PTR_s__box_uart_mgr_crc_check_failed__d_0053a3bc,uVar6,
                                  uVar7 & 0xff,
                                  *(undefined1 *)((uint)uVar5 + (uint)uVar6 + iVar1 + -1));
            }
            return 0xfffffffd;
          }
          FUN_00439be4(param_2,iVar1 + (uint)uVar5,uVar6);
          *param_3 = (char)uVar6;
        }
        break;
      }
    }
    uVar2 = 0;
  }
  return uVar2;
}

