
undefined4
FUN_1000568c(uint param_1,uint param_2,uint param_3,int param_4,uint param_5,uint param_6)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = uRam00000108;
  uVar1 = (param_6 & 7) << 0x10;
  uRam00000108 = uRam00000108 & 0xfff8ffff | uVar1;
  if (((param_3 & 0x7f) == 0) && ((param_2 & 7) == 0)) {
    if (param_1 == 1) {
      iRam00000110 = param_4 * 2;
      uRam00000104 = 0x800;
      uRam00000108 = uVar2 & 0xfff8ff10 | uVar1 | 3 | (param_5 & 3) << 2 | 0x40 | (param_2 & 1) << 7
                     | 0x20;
      uRam0000011c = 0;
      uRam00000114 = param_2;
      uRam00000120 = param_3;
    }
    else {
      if (param_1 != 2) {
        return 0xffffffff;
      }
      iRam00000134 = param_4 * 2;
      uRam00000104 = 0x1000;
      uRam00000108 = uVar2 & 0xfff810ff | uVar1 | 0x300 | (param_5 & 3) << 10 | 0x4000 |
                     (param_2 & 1) << 0xf | 0x2000;
      uRam00000140 = 0;
      uRam00000138 = param_2;
      uRam00000144 = param_3;
    }
    *(uint *)(DAT_10005790 + 4) = param_1 | *(uint *)(DAT_10005790 + 4);
    return 0;
  }
  return 0xffffffff;
}

