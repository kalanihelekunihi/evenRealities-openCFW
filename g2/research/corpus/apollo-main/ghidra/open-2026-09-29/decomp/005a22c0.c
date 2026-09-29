
uint FUN_005a22c0(int param_1,int param_2,undefined4 param_3)

{
  byte bVar1;
  uint *puVar2;
  uint *puVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  undefined4 local_28;
  
  iVar6 = DAT_005a2af8;
  puVar3 = (uint *)(DAT_005a2af8 + param_1 * 4 + 4);
  puVar2 = (uint *)(DAT_005a2af8 + 100);
  local_28 = CONCAT13((char)(*puVar2 >> 0x15),
                      CONCAT12((char)(*puVar2 >> 0xe),
                               CONCAT11((char)(*puVar2 >> 7),*(undefined1 *)puVar2))) & 0x7f7f7f7f;
  uVar4 = (*(uint *)(DAT_005a2af8 + param_2 * 4 + 4) & 0xfffffff) >> 0x15;
  uVar5 = (*puVar3 & 0xfffffff) >> 0x15;
  bVar1 = *(byte *)puVar3;
  if (*DAT_005a2afc << 0x1f < 0) {
    uVar7 = 0;
    while ((uVar7 < 0x3c && (-1 < *DAT_005a2b04 << 1))) {
      FUN_004807a0(1);
      uVar7 = uVar7 + 1;
    }
    FUN_005a40ca();
  }
  *DAT_005a2b08 = param_3;
  *DAT_005a2b0c = param_1;
  *DAT_005a2d10 = (*puVar3 & 0x1ffff) >> 7;
  *DAT_005a2d14 = (*puVar3 & 0x1fffff) >> 0x11;
  *DAT_005a2d18 = uVar5;
  *DAT_005a2b10 = bVar1 & 0x7f;
  FUN_005a423c(param_3,param_1);
  *DAT_005a2c28 = *DAT_005a2c28 & 0xffffff80 | *(uint *)(iVar6 + 0x50) & 0x7f;
  iVar6 = uVar5 - uVar4;
  if (iVar6 < 1) {
    iVar6 = 0;
  }
  else {
    iVar6 = iVar6 * 2;
  }
  if (iVar6 + uVar4 < 0x80) {
    *DAT_005a2d04 = *DAT_005a2d04 & 0xffffff80 | iVar6 + uVar4 & 0x7f;
  }
  else {
    *DAT_005a2d04 = *DAT_005a2d04 | 0x7f;
  }
  *DAT_005a2b00 = param_1;
  FUN_00480240(0x32);
  *DAT_005a2d08 = 2;
  return local_28;
}

