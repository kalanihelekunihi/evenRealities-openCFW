
uint FUN_005a2586(int param_1,undefined4 param_2,undefined4 param_3)

{
  byte bVar1;
  uint *puVar2;
  uint *puVar3;
  uint uVar4;
  uint uVar5;
  undefined4 local_20;
  
  puVar3 = (uint *)(DAT_005a2af8 + param_1 * 4 + 4);
  puVar2 = (uint *)(DAT_005a2af8 + 100);
  local_20 = CONCAT13((char)(*puVar2 >> 0x15),
                      CONCAT12((char)(*puVar2 >> 0xe),
                               CONCAT11((char)(*puVar2 >> 7),*(undefined1 *)puVar2))) & 0x7f7f7f7f;
  uVar4 = (*puVar3 & 0xfffffff) >> 0x15;
  bVar1 = *(byte *)puVar3;
  if (*DAT_005a2afc << 0x1f < 0) {
    uVar5 = 0;
    while ((uVar5 < 0x3c && (-1 < *DAT_005a2b04 << 1))) {
      FUN_004807a0(1);
      uVar5 = uVar5 + 1;
    }
    FUN_005a40ca();
  }
  *DAT_005a2b08 = param_3;
  *DAT_005a2b0c = param_1;
  *DAT_005a2d10 = (*puVar3 & 0x1ffff) >> 7;
  *DAT_005a2d14 = (*puVar3 & 0x1fffff) >> 0x11;
  *DAT_005a2d18 = uVar4;
  *DAT_005a2b10 = bVar1 & 0x7f;
  puVar2 = DAT_005a2d20;
  *DAT_005a2d20 = *DAT_005a2d20 & 0xffffc3ff | ((*puVar3 & 0x1fffff) >> 0x11) << 10;
  *puVar2 = (*puVar3 & 0x1ffff) >> 7 | *puVar2 & 0xfffffc00;
  *DAT_005a2d04 = uVar4 | *DAT_005a2d04 & 0xffffff80;
  *DAT_005a2c28 = bVar1 & 0x7f | *DAT_005a2c28 & 0xffffff80;
  FUN_005a423c(param_3,param_1);
  puVar2 = DAT_005a2d1c;
  *DAT_005a2d1c = *DAT_005a2d1c & 0xfffffff7;
  *puVar2 = *puVar2 & 0xffffffbf;
  *puVar2 = *puVar2 & 0xfffeffff;
  return local_20;
}

