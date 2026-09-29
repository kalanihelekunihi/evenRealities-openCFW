
uint FUN_005a1f04(int param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  uint *puVar2;
  uint *puVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  bool bVar8;
  uint local_28;
  
  puVar3 = (uint *)(DAT_005a2af8 + param_1 * 4 + 4);
  puVar2 = (uint *)(DAT_005a2af8 + 100);
  local_28 = CONCAT13((char)(*puVar2 >> 0x15),
                      CONCAT12((char)(*puVar2 >> 0xe),
                               CONCAT11((char)(*puVar2 >> 7),*(undefined1 *)puVar2))) & 0x7f7f7f7f;
  uVar4 = *(byte *)(DAT_005a2af8 + param_2 * 4 + 4) & 0x7f;
  uVar5 = (*puVar3 & 0xfffffff) >> 0x15;
  uVar6 = *(byte *)puVar3 & 0x7f;
  if (*DAT_005a2afc << 0x1f < 0) {
    if (param_1 == *DAT_005a2b00) {
      FUN_005a423c(param_3,param_1);
      *DAT_005a2d04 = uVar5 | *DAT_005a2d04 & 0xffffff80;
      FUN_004802ce();
      *DAT_005a2d08 = 0x1a;
      return local_28;
    }
    if (*DAT_005a2afc << 0x1f < 0) {
      uVar7 = 0;
      while ((uVar7 < 0x3c && (-1 < *DAT_005a2b04 << 1))) {
        FUN_004807a0(1);
        uVar7 = uVar7 + 1;
      }
      FUN_005a40ca();
    }
  }
  *DAT_005a2b08 = param_3;
  *DAT_005a2b0c = param_1;
  *DAT_005a2d10 = (*puVar3 & 0x1ffff) >> 7;
  *DAT_005a2d14 = (*puVar3 & 0x1fffff) >> 0x11;
  *DAT_005a2d18 = uVar5;
  *DAT_005a2b10 = uVar6;
  FUN_005a423c(param_3,param_1);
  if ((int)(uVar6 - uVar4) < 1) {
    iVar1 = 0;
  }
  else {
    iVar1 = (uVar6 - uVar4) * 2;
  }
  if (iVar1 + uVar4 < 0x80) {
    *DAT_005a2c28 = *DAT_005a2c28 & 0xffffff80 | iVar1 + uVar4 & 0x7f;
  }
  else {
    *DAT_005a2c28 = *DAT_005a2c28 | 0x7f;
  }
  FUN_004807a0(0x32);
  *DAT_005a2c28 = uVar6 | *DAT_005a2c28 & 0xffffff80;
  bVar8 = *DAT_005a2c2c << 0xe < 0;
  if (bVar8) {
    FUN_00474efa();
  }
  puVar2 = DAT_005a2d1c;
  *DAT_005a2d1c = *DAT_005a2d1c | 0x10000;
  *puVar2 = *puVar2 | 0x2000000;
  FUN_004807a0(0x14);
  if (bVar8) {
    FUN_00474eb4();
  }
  puVar2 = DAT_005a2d20;
  *DAT_005a2d20 = *DAT_005a2d20 & 0xffffc3ff | ((*puVar3 & 0x1fffff) >> 0x11) << 10;
  *puVar2 = (*puVar3 & 0x1ffff) >> 7 | *puVar2 & 0xfffffc00;
  *DAT_005a2d04 = uVar5 | *DAT_005a2d04 & 0xffffff80;
  return local_28;
}

