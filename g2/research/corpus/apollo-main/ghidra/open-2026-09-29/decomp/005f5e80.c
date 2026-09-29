
undefined4 Ins_SZP1(int param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  if (*param_2 == 0) {
    FUN_00439c04(param_1 + 0x48,param_1 + 0xb4,0x24);
  }
  else {
    if (*param_2 != 1) {
      if (*(char *)(param_1 + 0x235) == '\0') {
        return param_4;
      }
      *(undefined4 *)(param_1 + 0xc) = 0x86;
      return param_4;
    }
    FUN_00439c04(param_1 + 0x48,param_1 + 0x90,0x24);
  }
  *(short *)(param_1 + 0x15e) = (short)*param_2;
  return param_4;
}

