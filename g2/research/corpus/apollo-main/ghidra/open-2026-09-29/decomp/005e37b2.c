
undefined4 smpiScActDHKeyCheckSend(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  smpLogByteArray(PTR_s_DHKey_Eb_005e38c0,*(undefined4 *)(param_2 + 4),0x10);
  WStrReverseCpy(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10,*(undefined4 *)(param_2 + 4),0x10)
  ;
  *(undefined1 *)(param_1 + 0x3f) = 0xd;
  smpScSendDHKeyCheck(param_1,param_2,*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14));
  return param_4;
}

