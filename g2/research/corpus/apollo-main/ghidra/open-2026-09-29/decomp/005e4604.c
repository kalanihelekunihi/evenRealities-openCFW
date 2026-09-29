
undefined4
terminal_data_recv_handler(char *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  
  if (param_1 == (char *)0x0) {
    uVar2 = 0xffffffff;
  }
  else {
    cVar1 = *param_1;
    if (cVar1 == '\x01') {
      uVar2 = terminal_machine_handler(1,param_1 + 4,2,param_4,param_1,param_2,param_3,param_4);
    }
    else if (cVar1 == '\x02') {
      uVar2 = terminal_machine_handler(2,param_1 + 4,2,param_4,param_1,param_2,param_3,param_4);
    }
    else if (cVar1 == '\x03') {
      uVar2 = terminal_machine_handler(3,param_1 + 4,0x204,param_4,param_1,param_2,param_3,param_4);
    }
    else if (cVar1 == '\x04') {
      uVar2 = terminal_machine_handler(4,param_1 + 4,8,param_4,param_1,param_2,param_3,param_4);
    }
    else if (cVar1 == '\x05') {
      uVar2 = terminal_machine_handler(5,param_1 + 4,0x214,param_4,param_1,param_2,param_3,param_4);
    }
    else if (cVar1 == '\x06') {
      uVar2 = terminal_machine_handler(6,param_1 + 4,0x84c,param_4,param_1,param_2,param_3,param_4);
    }
    else if (cVar1 == '\a') {
      uVar2 = terminal_machine_handler(8,param_1 + 4,1,param_4,param_1,param_2,param_3,param_4);
    }
    else if (cVar1 == '\b') {
      uVar2 = terminal_machine_handler(9,param_1 + 4,0x55c,param_4,param_1,param_2,param_3,param_4);
    }
    else if (cVar1 == '\t') {
      uVar2 = terminal_machine_handler(10,param_1 + 4,1,param_4,param_1,param_2,param_3,param_4);
    }
    else if (cVar1 == '\n') {
      uVar2 = terminal_machine_handler(0xc,param_1 + 4,4,param_4,param_1,param_2,param_3,param_4);
    }
    else if (cVar1 == '\v') {
      uVar2 = terminal_machine_handler(0xb,param_1 + 4,1,param_4,param_1,param_2,param_3,param_4);
    }
    else if (cVar1 == -0x5d) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(3,DAT_005e477c,DAT_005e4778,PTR_s_terminal_data_recv_handler_005e47bc,0xe3,
                     PTR_s_ignore_terminal_query_reply_from_005e47b8);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__terminal_ignore_terminal_query_r_005e47c0);
      }
      uVar2 = 0;
    }
    else if (cVar1 == -1) {
      uVar2 = terminal_machine_handler(7,param_1 + 4,1,param_4,param_1,param_2,param_3,param_4);
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(2,DAT_005e477c,DAT_005e4778,PTR_s_terminal_data_recv_handler_005e47bc,0xf5,
                     PTR_s_unsupported_terminal_command_id__005e47c4,*param_1);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__terminal_unsupported_terminal_c_005e47c8,
                            PTR_s__terminal_unsupported_terminal_c_005e47c8,*param_1);
      }
      uVar2 = 0xffffffff;
    }
  }
  return uVar2;
}

