
undefined4 state_register_initialize_42d3bc(void)

{
  uint *puVar1;
  uint *puVar2;
  uint *puVar3;
  uint *puVar4;
  uint uVar5;
  int iVar6;
  
  puVar1 = DAT_0042d7e0;
  if ((*DAT_0042d7a4 & 0x3f) >> 4 == 3) {
    if ((*DAT_0042d7e0 & 0x3ff) + 0xc < 0x400) {
      iVar6 = 0xc;
    }
    else {
      iVar6 = 0x3ff - (*DAT_0042d7e0 & 0x3ff);
    }
    *DAT_0042d7e0 = iVar6 + *DAT_0042d7e0 & 0x3ff | *DAT_0042d7e0 & 0xfffffc00;
    puVar2 = DAT_0042d7e8;
    *DAT_0042d7e8 = *DAT_0042d7e8 & 0xffffffc0 | 5;
    delay_us(5);
    puVar3 = DAT_0042d7f4;
    *DAT_0042d7f4 = *DAT_0042d7f4 | 0x20000000;
    *puVar3 = *puVar3 | 0x10000000;
    *puVar3 = *puVar3 | 0x80000000;
    *puVar3 = *puVar3 | 0x40000000;
    delay_us(10);
    puVar4 = DAT_0042d800;
    *DAT_0042d800 = *DAT_0042d800 & 0xc1ffffff | 0xc000000;
    *puVar4 = *puVar4 & 0xffff07ff | 0x3000;
    puVar4 = DAT_0042d804;
    *DAT_0042d804 = *DAT_0042d804 & 0xc1ffffff | 0xa000000;
    *puVar4 = *puVar4 & 0xffff07ff | 0x2800;
    *DAT_0042d808 = *DAT_0042d808 & 0xffffe0ff | 0x700;
    *DAT_0042d80c = *DAT_0042d80c & 0xffc1ffff | 0x140000;
    if (*DAT_0042d7ac != '\0') {
      if ((*DAT_0042d7b4 & 0x7f) < 0x10) {
        uVar5 = 0;
      }
      else {
        uVar5 = (*DAT_0042d7b4 & 0x7f) - 0xf;
      }
      *DAT_0042d7b4 = *DAT_0042d7b4 & 0xffffff80 | uVar5 & 0x7f;
      if ((*DAT_0042d7f8 & 0x7f) < 10) {
        uVar5 = 0;
      }
      else {
        uVar5 = (*DAT_0042d7f8 & 0x7f) - 9;
      }
      *DAT_0042d7f8 = *DAT_0042d7f8 & 0xffffff80 | uVar5 & 0x7f;
      *puVar1 = *puVar1 & 0xffffc3ff | (*DAT_0042d7f0 & 0xf) << 10;
      *DAT_0042d7fc = *DAT_0042d7fc & 0xfffffeff;
    }
    *puVar1 = *puVar1 - iVar6 & 0x3ff | *puVar1 & 0xfffffc00;
    if (*DAT_0042d810 == '\0') {
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
    *DAT_0042d7e8 = *DAT_0042d7e8 & 0xffffffc0 | *DAT_0042d7ec & 0x3f;
    *DAT_0042d7e0 = *DAT_0042d7e0 & 0xffffc3ff | (*DAT_0042d7e4 & 0xf) << 10;
  }
  return 0;
}

