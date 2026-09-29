
undefined4 FUN_10005490(int param_1,uint param_2,uint param_3)

{
  if (param_1 == 4) {
    uRam00000048 = uRam00000048 & 0xfffffff0 | param_2 & 0xf;
    uRam0000004c = uRam0000004c & 0xfffffff0 | param_3 & 0xf;
    return 0;
  }
  if (param_1 != 2) {
    return 0;
  }
  uRam00000028 = uRam00000028 & 0xfffffff0 | param_2 & 0xf;
  uRam0000002c = uRam0000002c & 0xfffffff0 | param_3 & 0xf;
  return 0;
}

