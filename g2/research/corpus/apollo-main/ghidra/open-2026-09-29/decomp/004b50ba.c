
undefined4 attL2cDataReq(int param_1,char param_2,undefined2 param_3,undefined4 param_4)

{
  if (param_2 == '\0') {
    L2cDataReq(4,*(undefined2 *)(param_1 + 0xc),param_3);
  }
  else if (*(int *)(DAT_004b51d0 + 0x54) == 0) {
    WsfMsgFree(param_4);
  }
  else {
    (**(code **)(DAT_004b51d0 + 0x54))(param_1,param_2,param_3);
  }
  return param_4;
}

