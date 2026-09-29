
undefined4 FUN_005a0328(char param_1)

{
  char *pcVar1;
  uint *puVar2;
  uint *puVar3;
  uint *puVar4;
  uint *puVar5;
  uint uVar6;
  int iVar7;
  
  puVar2 = DAT_005a0a04;
  pcVar1 = DAT_005a09d0;
  if ((*DAT_005a09c8 & 0x3f) >> 4 == 3) {
    if (*DAT_005a09d0 != '\0') {
      *DAT_005a0a14 = (*DAT_005a0a04 & 0x3fff) >> 10;
      *puVar2 = *puVar2 & 0xffffc3ff | 0x400;
    }
    puVar2 = DAT_005a0a04;
    if ((*DAT_005a0a04 & 0x3ff) + 0xc < 0x400) {
      iVar7 = 0xc;
    }
    else {
      iVar7 = 0x3ff - (*DAT_005a0a04 & 0x3ff);
    }
    *DAT_005a0a04 = iVar7 + *DAT_005a0a04 & 0x3ff | *DAT_005a0a04 & 0xfffffc00;
    puVar3 = DAT_005a0a0c;
    *DAT_005a0a0c = *DAT_005a0a0c & 0xffffffc0 | 5;
    FUN_004807a0(5);
    if (*pcVar1 != '\0') {
      if ((*DAT_005a09d8 & 0x7f) + 0xf < 0x80) {
        uVar6 = (*DAT_005a09d8 & 0x7f) + 0xf;
      }
      else {
        uVar6 = 0x7f;
      }
      *DAT_005a09d8 = *DAT_005a09d8 & 0xffffff80 | uVar6 & 0x7f;
    }
    puVar4 = DAT_005a0a18;
    *DAT_005a0a18 = *DAT_005a0a18 | 0x20000000;
    *puVar4 = *puVar4 | 0x10000000;
    *puVar4 = *puVar4 | 0x80000000;
    *puVar4 = *puVar4 | 0x40000000;
    FUN_004807a0(10);
    if (*pcVar1 != '\0') {
      if ((*DAT_005a0a1c & 0x7f) + 9 < 0x80) {
        uVar6 = (*DAT_005a0a1c & 0x7f) + 9;
      }
      else {
        uVar6 = 0x7f;
      }
      *DAT_005a0a1c = *DAT_005a0a1c & 0xffffff80 | uVar6 & 0x7f;
      *DAT_005a0a20 = *DAT_005a0a20 | 0x100;
    }
    puVar5 = DAT_005a0a24;
    if (*pcVar1 == '\0') {
      *DAT_005a0a24 = *DAT_005a0a24 & 0xc1ffffff | 0xc000000;
      *puVar5 = *puVar5 & 0xffff07ff | 0x3000;
      puVar5 = DAT_005a0a28;
      *DAT_005a0a28 = *DAT_005a0a28 & 0xc1ffffff | 0xa000000;
      *puVar5 = *puVar5 & 0xffff07ff | 0x2800;
      if (param_1 == '\x01') {
        *DAT_005a0a2c = *DAT_005a0a2c & 0xffffe0ff | 0x900;
        *DAT_005a0a30 = *DAT_005a0a30 & 0xffc1ffff | 0x1a0000;
      }
      else {
        *DAT_005a0a2c = *DAT_005a0a2c & 0xffffe0ff | 0xd00;
        *DAT_005a0a30 = *DAT_005a0a30 & 0xffc1ffff | 0x260000;
      }
    }
    else {
      *DAT_005a0a24 = *DAT_005a0a24 & 0xc1ffffff | 0x14000000;
      *puVar5 = *puVar5 & 0xffff07ff | 0x5000;
      puVar5 = DAT_005a0a28;
      *DAT_005a0a28 = *DAT_005a0a28 & 0xc1ffffff | 0x10000000;
      *puVar5 = *puVar5 & 0xffff07ff | 0x4000;
      if (param_1 == '\x01') {
        *DAT_005a0a2c = *DAT_005a0a2c & 0xffffe0ff | 0x1000;
        *DAT_005a0a30 = *DAT_005a0a30 & 0xffc1ffff | 0x280000;
      }
      else {
        *DAT_005a0a2c = *DAT_005a0a2c & 0xffffe0ff | 0x1400;
        *DAT_005a0a30 = *DAT_005a0a30 & 0xffc1ffff | 0x2c0000;
      }
    }
    *puVar4 = *puVar4 & 0xdfffffff;
    *puVar4 = *puVar4 & 0xefffffff;
    *puVar4 = *puVar4 & 0x7fffffff;
    *puVar4 = *puVar4 & 0xbfffffff;
    uVar6 = *puVar2;
    *puVar2 = uVar6 - iVar7 & 0x3ff | uVar6 & 0xfffffc00;
    if (*DAT_005a0a34 == '\0') {
      *puVar3 = *puVar3 & 0xffffffc0 | 1;
    }
    else {
      *puVar3 = *puVar3 & 0xffffffc0;
    }
  }
  else {
    *DAT_005a0a08 = (*DAT_005a0a04 & 0x3fff) >> 10;
    *puVar2 = *puVar2 & 0xffffc3ff | 0x800;
    puVar2 = DAT_005a0a0c;
    *DAT_005a0a10 = *DAT_005a0a0c & 0x3f;
    if ((*puVar2 & 0x3f) + 5 < 0x40) {
      uVar6 = (*puVar2 & 0x3f) + 5;
    }
    else {
      uVar6 = 0x3f;
    }
    *puVar2 = *puVar2 & 0xffffffc0 | uVar6 & 0x3f;
    FUN_004807a0(0xf);
  }
  return 0;
}

