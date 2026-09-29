
int FUN_1000e2c4(int param_1,int param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  int iVar2;
  
  if (1 < param_2) {
    do {
      dsp_stub();
      if ((int)param_4 < 0) {
        param_4 = ~param_4 + 1;
      }
    } while (param_1 + param_2 * 2 != param_1 + 2);
  }
  iVar1 = 0;
  iVar2 = 0x20;
  do {
    if (0U >> (0x1fU - iVar1 & 0x3f) == 1) {
      return 0x11 - iVar1;
    }
    iVar1 = iVar1 + 1;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  return -0xf;
}

