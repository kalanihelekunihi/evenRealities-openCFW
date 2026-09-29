
int pxPortInitialiseStack(int param_1,undefined4 param_2,undefined4 param_3)

{
  *(undefined4 *)(param_1 + -4) = 0x1000000;
  *(undefined4 *)(param_1 + -8) = param_2;
  *(undefined4 *)(param_1 + -0xc) = DAT_0800b4dc;
  *(undefined4 *)(param_1 + -0x20) = param_3;
  return param_1 + -0x40;
}

