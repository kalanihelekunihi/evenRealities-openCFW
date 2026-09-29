
undefined4 smprScActWaitDhCheck(int param_1,undefined4 param_2)

{
  undefined4 unaff_r7;
  
  *(undefined1 *)(param_1 + 0x3f) = 0xd;
  if (*(char *)(*(int *)(param_1 + 0x48) + 1) == '\x03') {
    smpScSendRand(param_1,param_2,*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10);
  }
  return unaff_r7;
}

