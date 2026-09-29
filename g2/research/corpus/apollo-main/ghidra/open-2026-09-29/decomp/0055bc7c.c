
undefined4 dmConnUpdActL2cUpdateInd(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  L2cDmConnUpdateRsp(*(undefined1 *)(param_2 + 8),*(undefined2 *)(param_1 + 0xc),0);
  HciLeConnUpdateCmd(*(undefined2 *)(param_1 + 0xc),*(undefined4 *)(param_2 + 4));
  return param_4;
}

