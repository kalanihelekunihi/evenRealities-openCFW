
undefined4 smpiActCheckSecurityReq(int param_1,int param_2)

{
  undefined4 unaff_r7;
  
  if (*(char *)(param_1 + 0x3b) != '\0') {
    *(undefined1 *)(param_1 + 0x3b) = 0;
    smpSendPairingFailed(param_1,*(undefined1 *)(param_2 + 3));
  }
  return unaff_r7;
}

