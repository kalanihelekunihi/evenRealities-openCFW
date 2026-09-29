
undefined4
FUN_100054cc(uint param_1,uint param_2,uint param_3,uint param_4,undefined4 param_5,uint param_6,
            uint param_7)

{
  if (param_1 == 1) {
    if (((param_4 & 0x7f) == 0) && (((param_2 | param_3) & 7) == 0)) {
      uRam00000104 = 0x800;
      uRam00000108 = uRam00000108 & 0xffffff10 | param_7 & 3 | (param_6 & 3) << 2 | 0x40 |
                     ((param_2 | param_3) & 1) << 7 | 0x20;
      uRam00000110 = param_5;
      uRam00000114 = param_2;
      uRam0000011c = param_3;
      uRam00000120 = param_4;
      goto LAB_1000555e;
    }
  }
  else if (((param_1 == 2) && ((param_4 & 0x7f) == 0)) && (((param_2 | param_3) & 7) == 0)) {
    uRam00000134 = param_5;
    uRam00000104 = 0x1000;
    uRam00000108 = uRam00000108 & 0xffff10ff | (param_7 & 3) << 8 | (param_6 & 3) << 10 | 0x4000 |
                   ((param_2 | param_3) & 1) << 0xf | 0x2000;
    uRam00000138 = param_2;
    uRam00000140 = param_3;
    uRam00000144 = param_4;
LAB_1000555e:
    *(uint *)(DAT_100055dc + 4) = param_1 | *(uint *)(DAT_100055dc + 4);
    return 0;
  }
  return 0xffffffff;
}

