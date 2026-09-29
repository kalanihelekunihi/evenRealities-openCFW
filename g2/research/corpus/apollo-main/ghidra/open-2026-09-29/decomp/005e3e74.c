
undefined4
smprScActJwncDisplay(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  *(undefined1 *)(param_1 + 0x3f) = 0xd;
  smpScSendRand(param_1,param_2,*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10);
  smpScActJwncDisplay(param_1,param_2);
  return param_4;
}

