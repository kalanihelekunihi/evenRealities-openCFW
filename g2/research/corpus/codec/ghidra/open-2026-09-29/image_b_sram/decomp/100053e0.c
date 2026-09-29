
void FUN_100053e0(uint param_1,uint param_2,uint param_3,uint param_4,uint param_5,uint param_6)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  gx8002_platform_gate(2,1);
  uVar1 = (param_1 & 0xf) << 4;
  uVar2 = (param_2 & 7) << 8;
  uVar3 = (param_3 & 1) << 0x10;
  uVar4 = (param_4 & 3) << 0x12;
  uVar5 = (param_5 & 3) << 0x15;
  if (param_2 < 3) {
    uRam00000004 = uRam00000004 & 0xff90f80f | uVar1 | uVar2 | uVar3 | uVar4 | uVar5;
  }
  else {
    uRam00000004 = uRam00000004 & 0xff90f80f | uVar1 | uVar2 | uVar3 | uVar4 | uVar5 | 0x20000;
  }
  uRam00000004 = uRam00000004 & 0xbfeff7f3 | (param_6 & 1) << 0xb | 0x40000000;
  *DAT_1000548c = *DAT_1000548c | 4;
  return;
}

