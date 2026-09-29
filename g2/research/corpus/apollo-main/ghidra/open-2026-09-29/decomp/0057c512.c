
int gx8002_send_and_wait_response
              (undefined2 param_1,undefined2 param_2,undefined4 param_3,undefined2 param_4,
              undefined1 param_5,int param_6,undefined4 param_7)

{
  undefined4 uVar1;
  int iVar2;
  undefined2 local_1c [2];
  
  if (param_6 == 0) {
    iVar2 = -1;
  }
  else {
    gx8002_host_init();
    iVar2 = gx8002_send_message(param_1,param_2,param_3,param_4,param_5);
    uVar1 = DAT_0057ce6c;
    if (iVar2 == 0) {
      local_1c[0] = 0;
      iVar2 = gx8002_read_uart_data(DAT_0057ce6c,0x1e,local_1c,param_7);
      if (iVar2 == 0) {
        semantic_gx8002_uart_cleanup();
        iVar2 = gx8002_unpack_message(uVar1,local_1c[0],param_6);
        if (iVar2 == 0) {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0057c61c,DAT_0057c618,DAT_0057ce74,0x158,DAT_0057ce70,
                         *(undefined2 *)(param_6 + 4),*(ushort *)(param_6 + 4) >> 8,
                         *(undefined1 *)(param_6 + 4),*(undefined1 *)(param_6 + 6),
                         *(undefined1 *)(param_6 + 7));
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x11400000,DAT_0057d000,DAT_0057d000,*(undefined2 *)(param_6 + 4),
                                *(ushort *)(param_6 + 4) >> 8,*(undefined1 *)(param_6 + 4),
                                *(undefined1 *)(param_6 + 6),*(undefined1 *)(param_6 + 7));
          }
          iVar2 = 0;
        }
      }
      else {
        semantic_gx8002_uart_cleanup();
      }
    }
    else {
      semantic_gx8002_uart_cleanup();
    }
  }
  return iVar2;
}

