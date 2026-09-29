
undefined4 semantic_OtaNotifyStatus4(char param_1)

{
  undefined4 unaff_r7;
  
  if (param_1 == -0x3f) {
    unaff_r7 = 0x402;
    if (*DAT_00448868 == '\0') {
      Thread_MsgTransport3TxByBle(1,0xc1,&stack0xfffffff8,2);
    }
  }
  return unaff_r7;
}

