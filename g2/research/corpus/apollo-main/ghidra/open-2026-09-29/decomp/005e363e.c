
undefined4 smpiScActPkSendRand(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  WStrReverseCpy(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x40,*(int *)(param_2 + 4) + 9,0x10);
  *(undefined1 *)(param_1 + 0x3f) = 4;
  smpScSendRand(param_1,param_2,*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14));
  return param_4;
}

