
int SVC_CodecMicDelay1Bit(void)

{
  int iVar1;
  int iVar2;
  undefined4 in_r3;
  char local_10 [4];
  undefined4 uStack_c;
  
  uStack_c = in_r3;
  FUN_0043c0e4(local_10,1,0);
  iVar1 = GX8002_MicDelay1Bit(local_10,200);
  if ((iVar1 == 0) && (local_10[0] == '\x01')) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_codec_host_0057da2c,DAT_0057da28,DAT_0057dc00,0x34a,DAT_0057dc08);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__codec_host_CodecMicDelay1Bit_su_0057dc0c,
                          PTR_s__codec_host_CodecMicDelay1Bit_su_0057dc0c);
    }
    iVar1 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_codec_host_0057da2c,DAT_0057da28,DAT_0057dc00,0x347,DAT_0057dbfc,iVar1,
                   local_10[0]);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_0057dc04,DAT_0057dc04,iVar1,local_10[0]);
    }
  }
  return iVar1;
}

