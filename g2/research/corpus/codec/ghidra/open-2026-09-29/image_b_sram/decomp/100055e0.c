
undefined4 FUN_100055e0(uint param_1,uint param_2,uint param_3,uint param_4,uint param_5)

{
  uint uVar1;
  
  if ((((param_1 & 7) == 0) && (uVar1 = (param_2 / 0x50) * 0x50, param_2 == uVar1)) &&
     (param_2 == param_3 * (param_2 / param_3))) {
    uRam00000160 = param_1 & 0xfffffff8;
    uRam00000104 = 0x2000;
    uRam00000108 = uRam00000108 & 0xff00ffff | (param_4 & 3) << 0x13 | (param_5 & 7) << 0x10 |
                   0x600000;
    uRam0000015c = param_3;
    uRam00000164 = uVar1;
    *(uint *)(DAT_10005688 + 4) = *(uint *)(DAT_10005688 + 4) | 4;
    return 0;
  }
  return 0xffffffff;
}

