
undefined4 FUN_005a2b14(void)

{
  uint *puVar1;
  uint *puVar2;
  undefined4 in_r3;
  uint uVar3;
  bool bVar4;
  
  *DAT_005a2d04 = *DAT_005a2d04 & 0xffffff80 | *DAT_005a2d18 & 0x7f;
  puVar2 = DAT_005a2d20;
  *DAT_005a2d20 = *DAT_005a2d20 & 0xffffc3ff | (*DAT_005a2d14 & 0xf) << 10;
  *puVar2 = *puVar2 & 0xfffffc00 | *DAT_005a2d10 & 0x3ff;
  FUN_004807a0(5);
  *DAT_005a2c28 = *DAT_005a2c28 & 0xffffff80 | *DAT_005a35a0 & 0x7f;
  puVar2 = DAT_005a3260;
  if ((*DAT_005a3260 & 3) == 2) {
    *DAT_005a3260 = *DAT_005a3260 & 0xfffffffc | 1;
    uVar3 = 0;
    while ((uVar3 < 0x14 && ((*puVar2 & 7) >> 2 == 0))) {
      FUN_004807a0(1);
      uVar3 = uVar3 + 1;
    }
    bVar4 = true;
  }
  else {
    bVar4 = false;
  }
  puVar1 = DAT_005a2d1c;
  *DAT_005a2d1c = *DAT_005a2d1c | 0x40;
  *puVar1 = *puVar1 | 8;
  *puVar1 = *puVar1 & 0xfdffffff;
  puVar1 = DAT_005a3264;
  if (bVar4) {
    bVar4 = -1 < (int)(*DAT_005a3264 << 0x1a);
    if (bVar4) {
      *DAT_005a3264 = *DAT_005a3264 | 0x20;
      FUN_004807a0(1);
      FUN_004807fc(0xf,DAT_005a3268,0x1000000,0x1000000);
    }
    if (*DAT_005a3268 << 7 < 0) {
      *puVar2 = *puVar2 & 0xfffffffc | 2;
      uVar3 = 0;
      while ((uVar3 < 0x14 && ((*puVar2 & 7) >> 2 == 0))) {
        FUN_004807a0(1);
        uVar3 = uVar3 + 1;
      }
    }
    if (bVar4) {
      *puVar1 = *puVar1 & 0xffffffdf;
    }
  }
  *DAT_005a2d08 = 0x1a;
  return in_r3;
}

