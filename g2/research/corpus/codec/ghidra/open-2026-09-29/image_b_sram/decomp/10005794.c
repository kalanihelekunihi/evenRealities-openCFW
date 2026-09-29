
undefined4
FUN_10005794(uint param_1,uint param_2,uint param_3,uint param_4,uint param_5,uint param_6,
            uint param_7)

{
  undefined4 uVar1;
  
  gx8002_platform_gate(2,1);
  uVar1 = 0;
  if (((param_4 < 2) && (param_2 < 3)) && (param_1 != 8)) {
    uRam00000008 = uRam00000008 & 0x3fff0000 | param_1 & 3 | (param_2 & 3) << 2 | (param_3 & 1) << 4
                   | (param_4 & 1) << 5 | (param_5 & 3) << 6 | (param_6 & 0xf) << 8 |
                   (param_7 & 0xf) << 0xc | 0x40000000;
    *(uint *)(DAT_1000583c + 4) = *(uint *)(DAT_1000583c + 4) | 8;
    uRam00000008 = uRam00000008 & 0xfffeffff | 0x10000;
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

