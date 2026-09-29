
int GX8002_MicDelay1Bit(undefined1 *param_1,undefined4 param_2)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined2 local_48 [2];
  undefined1 auStack_44 [14];
  undefined1 *local_36;
  short local_32;
  undefined1 auStack_28 [16];
  
  if (param_1 == (undefined1 *)0x0) {
    iVar2 = -1;
  }
  else {
    iVar2 = -1;
    for (iVar4 = 0; iVar4 < 3; iVar4 = iVar4 + 1) {
      FUN_0043c0e4(auStack_44,0x1a,0);
      gx8002_host_init();
      FUN_00439c04(auStack_28,DAT_0057db70,0x10);
      iVar2 = FUN_0058fb38(auStack_28,0xe);
      uVar1 = DAT_0057db7c;
      if (iVar2 == 0) {
        local_48[0] = 0;
        iVar2 = gx8002_read_uart_data(DAT_0057db7c,0x1e,local_48,param_2);
        if (iVar2 == 0) {
          semantic_gx8002_uart_cleanup();
          iVar2 = gx8002_unpack_message(uVar1,local_48[0],auStack_44);
          if (iVar2 == 0) break;
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(2,PTR_s_codec_host_0057da2c,DAT_0057da28,DAT_0057db68,0x2d5,DAT_0057db64,
                         iVar4 + 1,iVar2);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x8800000,DAT_0057db6c,DAT_0057db6c,iVar4 + 1,iVar2);
          }
          semantic_gx8002_free_message(auStack_44);
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_codec_host_0057da2c,DAT_0057da28,DAT_0057db68,0x2c8,DAT_0057db80,
                         iVar2);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x4400000,DAT_0057db84,DAT_0057db84,iVar2);
          }
          semantic_gx8002_uart_cleanup();
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_codec_host_0057da2c,DAT_0057da28,DAT_0057db68,0x2bf,DAT_0057db74,
                       iVar2);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_0057db78,DAT_0057db78,iVar2);
        }
        semantic_gx8002_uart_cleanup();
      }
    }
    if (iVar2 == 0) {
      if (local_32 == 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_codec_host_0057da2c,DAT_0057da28,DAT_0057db68,0x2e1,DAT_0057db90,
                       local_32);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4400000,PTR_s__codec_host_Invalid_mic_delay_1b_0057db94,
                              PTR_s__codec_host_Invalid_mic_delay_1b_0057db94,local_32);
        }
        semantic_gx8002_free_message(auStack_44);
        iVar2 = -1;
      }
      else {
        *param_1 = *local_36;
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_codec_host_0057da2c,DAT_0057da28,DAT_0057db68,0x2e6,DAT_0057db88,
                       *param_1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_0057db8c,DAT_0057db8c,*param_1);
        }
        semantic_gx8002_free_message(auStack_44);
        iVar2 = 0;
      }
    }
  }
  return iVar2;
}

