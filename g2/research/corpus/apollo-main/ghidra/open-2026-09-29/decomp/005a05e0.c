
undefined4 FUN_005a05e0(void)

{
  uint *puVar1;
  uint *puVar2;
  uint *puVar3;
  uint *puVar4;
  uint uVar5;
  int iVar6;
  
  puVar1 = DAT_005a0a04;
  if ((*DAT_005a09c8 & 0x3f) >> 4 == 3) {
    if ((*DAT_005a0a04 & 0x3ff) + 0xc < 0x400) {
      iVar6 = 0xc;
    }
    else {
      iVar6 = 0x3ff - (*DAT_005a0a04 & 0x3ff);
    }
    *DAT_005a0a04 = iVar6 + *DAT_005a0a04 & 0x3ff | *DAT_005a0a04 & 0xfffffc00;
    puVar2 = DAT_005a0a0c;
    *DAT_005a0a0c = *DAT_005a0a0c & 0xffffffc0 | 5;
    FUN_004807a0(5);
    puVar3 = DAT_005a0a18;
    *DAT_005a0a18 = *DAT_005a0a18 | 0x20000000;
    *puVar3 = *puVar3 | 0x10000000;
    *puVar3 = *puVar3 | 0x80000000;
    *puVar3 = *puVar3 | 0x40000000;
    FUN_004807a0(10);
    puVar4 = DAT_005a0a24;
    *DAT_005a0a24 = *DAT_005a0a24 & 0xc1ffffff | 0xc000000;
    *puVar4 = *puVar4 & 0xffff07ff | 0x3000;
    puVar4 = DAT_005a0a28;
    *DAT_005a0a28 = *DAT_005a0a28 & 0xc1ffffff | 0xa000000;
    *puVar4 = *puVar4 & 0xffff07ff | 0x2800;
    *DAT_005a0a2c = *DAT_005a0a2c & 0xffffe0ff | 0x700;
    *DAT_005a0a30 = *DAT_005a0a30 & 0xffc1ffff | 0x140000;
    if (*DAT_005a09d0 != '\0') {
      if ((*DAT_005a09d8 & 0x7f) < 0x10) {
        uVar5 = 0;
      }
      else {
        uVar5 = (*DAT_005a09d8 & 0x7f) - 0xf;
      }
      *DAT_005a09d8 = *DAT_005a09d8 & 0xffffff80 | uVar5 & 0x7f;
      if ((*DAT_005a0a1c & 0x7f) < 10) {
        uVar5 = 0;
      }
      else {
        uVar5 = (*DAT_005a0a1c & 0x7f) - 9;
      }
      *DAT_005a0a1c = *DAT_005a0a1c & 0xffffff80 | uVar5 & 0x7f;
      *puVar1 = *puVar1 & 0xffffc3ff | (*DAT_005a0a14 & 0xf) << 10;
      *DAT_005a0a20 = *DAT_005a0a20 & 0xfffffeff;
    }
    *puVar1 = *puVar1 - iVar6 & 0x3ff | *puVar1 & 0xfffffc00;
    if (*DAT_005a0a34 == '\0') {
      *puVar2 = *puVar2 & 0xffffffc0 | 1;
    }
    else {
      *puVar2 = *puVar2 & 0xffffffc0;
    }
    *puVar3 = *puVar3 & 0xdfffffff;
    *puVar3 = *puVar3 & 0xefffffff;
    *puVar3 = *puVar3 & 0x7fffffff;
    *puVar3 = *puVar3 & 0xbfffffff;
  }
  else {
    *DAT_005a0a0c = *DAT_005a0a0c & 0xffffffc0 | *DAT_005a0a10 & 0x3f;
    *DAT_005a0a04 = *DAT_005a0a04 & 0xffffc3ff | (*DAT_005a0a08 & 0xf) << 10;
  }
  return 0;
}

