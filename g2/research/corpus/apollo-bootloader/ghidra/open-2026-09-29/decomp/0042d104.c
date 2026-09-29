
undefined4 state_event_one_value_42d104(char param_1)

{
  char *pcVar1;
  uint *puVar2;
  uint *puVar3;
  uint *puVar4;
  uint *puVar5;
  uint uVar6;
  int iVar7;
  
  puVar2 = DAT_0042d7e0;
  pcVar1 = DAT_0042d7ac;
  if ((*DAT_0042d7a4 & 0x3f) >> 4 == 3) {
    if (*DAT_0042d7ac != '\0') {
      *DAT_0042d7f0 = (*DAT_0042d7e0 & 0x3fff) >> 10;
      *puVar2 = *puVar2 & 0xffffc3ff | 0x400;
    }
    puVar2 = DAT_0042d7e0;
    if ((*DAT_0042d7e0 & 0x3ff) + 0xc < 0x400) {
      iVar7 = 0xc;
    }
    else {
      iVar7 = 0x3ff - (*DAT_0042d7e0 & 0x3ff);
    }
    *DAT_0042d7e0 = iVar7 + *DAT_0042d7e0 & 0x3ff | *DAT_0042d7e0 & 0xfffffc00;
    puVar3 = DAT_0042d7e8;
    *DAT_0042d7e8 = *DAT_0042d7e8 & 0xffffffc0 | 5;
    delay_us(5);
    if (*pcVar1 != '\0') {
      if ((*DAT_0042d7b4 & 0x7f) + 0xf < 0x80) {
        uVar6 = (*DAT_0042d7b4 & 0x7f) + 0xf;
      }
      else {
        uVar6 = 0x7f;
      }
      *DAT_0042d7b4 = *DAT_0042d7b4 & 0xffffff80 | uVar6 & 0x7f;
    }
    puVar4 = DAT_0042d7f4;
    *DAT_0042d7f4 = *DAT_0042d7f4 | 0x20000000;
    *puVar4 = *puVar4 | 0x10000000;
    *puVar4 = *puVar4 | 0x80000000;
    *puVar4 = *puVar4 | 0x40000000;
    delay_us(10);
    if (*pcVar1 != '\0') {
      if ((*DAT_0042d7f8 & 0x7f) + 9 < 0x80) {
        uVar6 = (*DAT_0042d7f8 & 0x7f) + 9;
      }
      else {
        uVar6 = 0x7f;
      }
      *DAT_0042d7f8 = *DAT_0042d7f8 & 0xffffff80 | uVar6 & 0x7f;
      *DAT_0042d7fc = *DAT_0042d7fc | 0x100;
    }
    puVar5 = DAT_0042d800;
    if (*pcVar1 == '\0') {
      *DAT_0042d800 = *DAT_0042d800 & 0xc1ffffff | 0xc000000;
      *puVar5 = *puVar5 & 0xffff07ff | 0x3000;
      puVar5 = DAT_0042d804;
      *DAT_0042d804 = *DAT_0042d804 & 0xc1ffffff | 0xa000000;
      *puVar5 = *puVar5 & 0xffff07ff | 0x2800;
      if (param_1 == '\x01') {
        *DAT_0042d808 = *DAT_0042d808 & 0xffffe0ff | 0x900;
        *DAT_0042d80c = *DAT_0042d80c & 0xffc1ffff | 0x1a0000;
      }
      else {
        *DAT_0042d808 = *DAT_0042d808 & 0xffffe0ff | 0xd00;
        *DAT_0042d80c = *DAT_0042d80c & 0xffc1ffff | 0x260000;
      }
    }
    else {
      *DAT_0042d800 = *DAT_0042d800 & 0xc1ffffff | 0x14000000;
      *puVar5 = *puVar5 & 0xffff07ff | 0x5000;
      puVar5 = DAT_0042d804;
      *DAT_0042d804 = *DAT_0042d804 & 0xc1ffffff | 0x10000000;
      *puVar5 = *puVar5 & 0xffff07ff | 0x4000;
      if (param_1 == '\x01') {
        *DAT_0042d808 = *DAT_0042d808 & 0xffffe0ff | 0x1000;
        *DAT_0042d80c = *DAT_0042d80c & 0xffc1ffff | 0x280000;
      }
      else {
        *DAT_0042d808 = *DAT_0042d808 & 0xffffe0ff | 0x1400;
        *DAT_0042d80c = *DAT_0042d80c & 0xffc1ffff | 0x2c0000;
      }
    }
    *puVar4 = *puVar4 & 0xdfffffff;
    *puVar4 = *puVar4 & 0xefffffff;
    *puVar4 = *puVar4 & 0x7fffffff;
    *puVar4 = *puVar4 & 0xbfffffff;
    uVar6 = *puVar2;
    *puVar2 = uVar6 - iVar7 & 0x3ff | uVar6 & 0xfffffc00;
    if (*DAT_0042d810 == '\0') {
      *puVar3 = *puVar3 & 0xffffffc0 | 1;
    }
    else {
      *puVar3 = *puVar3 & 0xffffffc0;
    }
  }
  else {
    *DAT_0042d7e4 = (*DAT_0042d7e0 & 0x3fff) >> 10;
    *puVar2 = *puVar2 & 0xffffc3ff | 0x800;
    puVar2 = DAT_0042d7e8;
    *DAT_0042d7ec = *DAT_0042d7e8 & 0x3f;
    if ((*puVar2 & 0x3f) + 5 < 0x40) {
      uVar6 = (*puVar2 & 0x3f) + 5;
    }
    else {
      uVar6 = 0x3f;
    }
    *puVar2 = *puVar2 & 0xffffffc0 | uVar6 & 0x3f;
    delay_us(0xf);
  }
  return 0;
}

