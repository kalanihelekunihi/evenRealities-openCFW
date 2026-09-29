
undefined4 smpiScActSendPubKey(int param_1)

{
  undefined4 unaff_r7;
  
  *(undefined1 *)(param_1 + 0x3f) = 0xc;
  smpScSendPubKey();
  return unaff_r7;
}

