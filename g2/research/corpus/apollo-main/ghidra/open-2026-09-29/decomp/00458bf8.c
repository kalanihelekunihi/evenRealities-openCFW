
undefined4 semantic_EfsNotifyStatus5(char param_1)

{
  undefined4 unaff_r7;
  
  if (param_1 == -0x3b) {
    unaff_r7 = 0x501;
    Thread_MsgEfsTxByBle(1,0xc5,&stack0xfffffff8,2);
  }
  return unaff_r7;
}

