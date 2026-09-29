
uint FUN_005a26be(int param_1,undefined4 param_2,undefined4 param_3)

{
  byte bVar1;
  uint *puVar2;
  uint *puVar3;
  uint *puVar4;
  uint uVar5;
  uint uVar6;
  bool bVar7;
  uint local_20;
  
  puVar4 = (uint *)(DAT_005a2af8 + param_1 * 4 + 4);
  puVar3 = (uint *)(DAT_005a2af8 + 100);
  local_20 = CONCAT13((char)(*puVar3 >> 0x15),
                      CONCAT12((char)(*puVar3 >> 0xe),
                               CONCAT11((char)(*puVar3 >> 7),*(undefined1 *)puVar3))) & 0x7f7f7f7f;
  uVar5 = (*puVar4 & 0xfffffff) >> 0x15;
  bVar1 = *(byte *)puVar4;
  if (*DAT_005a2afc << 0x1f < 0) {
    if (param_1 == *DAT_005a2b00) {
      FUN_005a423c(param_3,param_1);
      *DAT_005a2d04 = uVar5 | *DAT_005a2d04 & 0xffffff80;
      FUN_004802ce();
      *DAT_005a2d08 = 0x1a;
      return local_20;
    }
    if (*DAT_005a2afc << 0x1f < 0) {
      uVar6 = 0;
      while ((uVar6 < 0x3c && (-1 < *DAT_005a2b04 << 1))) {
        FUN_004807a0(1);
        uVar6 = uVar6 + 1;
      }
      FUN_005a40ca();
    }
  }
  *DAT_005a2b08 = param_3;
  *DAT_005a2b0c = param_1;
  *DAT_005a2d10 = (*puVar4 & 0x1ffff) >> 7;
  *DAT_005a2d14 = (*puVar4 & 0x1fffff) >> 0x11;
  *DAT_005a2d18 = uVar5;
  *DAT_005a2b10 = bVar1 & 0x7f;
  FUN_005a423c(param_3,param_1);
  puVar3 = DAT_005a3260;
  *DAT_005a3260 = *DAT_005a3260 & 0xfffffffc | 1;
  uVar6 = 0;
  while ((puVar2 = DAT_005a2d1c, uVar6 < 0x14 && ((*puVar3 & 7) >> 2 == 0))) {
    FUN_004807a0(1);
    uVar6 = uVar6 + 1;
  }
  *DAT_005a2d1c = *DAT_005a2d1c & 0xfffffff7;
  *puVar2 = *puVar2 & 0xffffffbf;
  *puVar2 = *puVar2 | 0x2000000;
  puVar2 = DAT_005a3264;
  bVar7 = -1 < (int)(*DAT_005a3264 << 0x1a);
  if (bVar7) {
    *DAT_005a3264 = *DAT_005a3264 | 0x20;
    FUN_004807a0(1);
    FUN_004807fc(0xf,DAT_005a3268,0x1000000,0x1000000);
  }
  if (*DAT_005a3268 << 7 < 0) {
    *puVar3 = *puVar3 & 0xfffffffc | 2;
    uVar6 = 0;
    while ((uVar6 < 0x14 && ((*puVar3 & 7) >> 2 == 0))) {
      FUN_004807a0(1);
      uVar6 = uVar6 + 1;
    }
  }
  if (bVar7) {
    *puVar2 = *puVar2 & 0xffffffdf;
  }
  puVar3 = DAT_005a2d20;
  *DAT_005a2d20 = *DAT_005a2d20 & 0xffffc3ff | ((*puVar4 & 0x1fffff) >> 0x11) << 10;
  *puVar3 = (*puVar4 & 0x1ffff) >> 7 | *puVar3 & 0xfffffc00;
  *DAT_005a2d04 = uVar5 | *DAT_005a2d04 & 0xffffff80;
  return local_20;
}

