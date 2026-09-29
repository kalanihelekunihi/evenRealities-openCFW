
undefined4 FUN_100058bc(int param_1,int param_2)

{
  if (param_1 == 1) {
    uRam0000000c = uRam0000000c & 0xfffffeff | ((byte)~(param_2 != 0) & 1) << 8;
    return 0;
  }
  if (param_1 != 2) {
    if (param_1 != 4) {
      return 0;
    }
    uRam00000048 = uRam00000048 & 0xfffffeff | ((byte)~(param_2 != 0) & 1) << 8;
    uRam0000004c = uRam0000004c & 0xfffffeff | ((byte)~(param_2 != 0) & 1) << 8;
    return 0;
  }
  uRam00000028 = uRam00000028 & 0xfffffeff | ((byte)~(param_2 != 0) & 1) << 8;
  uRam0000002c = uRam0000002c & 0xfffffeff | ((byte)~(param_2 != 0) & 1) << 8;
  return 0;
}

