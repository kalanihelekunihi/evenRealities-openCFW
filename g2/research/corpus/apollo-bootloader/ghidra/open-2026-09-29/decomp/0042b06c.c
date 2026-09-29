
void spotmgr_power_transition_trims_42b06c(uint param_1,int param_2)

{
  uint *puVar1;
  uint *puVar2;
  uint *puVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  
  puVar2 = DAT_0042b6a8;
  puVar1 = DAT_0042b6a0;
  if ((*DAT_0042b6a8 & 0x3ff) + 0xe < 0x400) {
    iVar6 = 0xe;
  }
  else {
    iVar6 = 0x3ff - (*DAT_0042b6a8 & 0x3ff);
  }
  if ((*DAT_0042b6a0 & 0x3f) + 6 < 0x40) {
    iVar7 = 6;
  }
  else {
    iVar7 = 0x3f - (*DAT_0042b6a0 & 0x3f);
  }
  *DAT_0042b6a8 = iVar6 + *DAT_0042b6a8 & 0x3ff | *DAT_0042b6a8 & 0xfffffc00;
  *puVar1 = iVar7 + *puVar1 & 0x3f | *puVar1 & 0xffffffc0;
  delay_us(0x14);
  puVar3 = DAT_0042b9ec;
  *DAT_0042b9ec = *DAT_0042b9ec | 0x20000000;
  *puVar3 = *puVar3 | 0x10000000;
  delay_us(0x14);
  if (param_1 == 0) {
    uVar4 = *(byte *)(DAT_0042b6a4 + 0x5c) & 0x1f;
    uVar5 = (*(uint *)(DAT_0042b6a4 + 0x5c) & 0x7fff) >> 10;
  }
  else if (param_1 == 2) {
    uVar4 = *(byte *)(DAT_0042b6a4 + 0x54) & 0x1f;
    uVar5 = *(byte *)(DAT_0042b6a4 + 0x58) & 0x1f;
  }
  else if (param_1 < 2) {
    uVar4 = (*(uint *)(DAT_0042b6a4 + 0x5c) & 0x3ff) >> 5;
    uVar5 = (*(uint *)(DAT_0042b6a4 + 0x5c) & 0xfffff) >> 0xf;
  }
  else if (param_1 == 4) {
    uVar4 = (*(uint *)(DAT_0042b6a4 + 0x54) & 0x3ff) >> 5;
    uVar5 = (*(uint *)(DAT_0042b6a4 + 0x58) & 0x3ff) >> 5;
  }
  else if (param_1 < 4) {
    uVar4 = (*(uint *)(DAT_0042b6a4 + 0x54) & 0x7fff) >> 10;
    uVar5 = (*(uint *)(DAT_0042b6a4 + 0x58) & 0x7fff) >> 10;
  }
  else if (param_1 == 6) {
    uVar4 = *(byte *)(DAT_0042b6a4 + 0x60) & 0x1f;
    uVar5 = (*(uint *)(DAT_0042b6a4 + 0x60) & 0x7fff) >> 10;
  }
  else if (param_1 < 6) {
    uVar4 = (*(uint *)(DAT_0042b6a4 + 0x54) & 0xfffff) >> 0xf;
    uVar5 = (*(uint *)(DAT_0042b6a4 + 0x58) & 0xfffff) >> 0xf;
  }
  else if (param_1 == 7) {
    uVar4 = (*DAT_0042b9f0 & 0xffff) >> 0xb;
    uVar5 = (*DAT_0042b9f4 & 0x3fffff) >> 0x11;
  }
  else {
    uVar4 = (*(uint *)(DAT_0042b6a4 + 0x54) & 0xfffff) >> 0xf;
    uVar5 = (*(uint *)(DAT_0042b6a4 + 0x58) & 0xfffff) >> 0xf;
  }
  if (param_2 == 8) {
    uVar4 = (*(uint *)(DAT_0042b6a4 + 0x5c) & 0x1ffffff) >> 0x14;
  }
  else if (param_2 == 0xc) {
    uVar4 = (*(uint *)(DAT_0042b6a4 + 0x54) & 0x1ffffff) >> 0x14;
  }
  else if (param_2 == 0xe) {
    if (uVar4 + 6 < 0x20) {
      uVar4 = uVar4 + 6;
    }
    else {
      uVar4 = 0x1f;
    }
  }
  else if (param_2 == 0xf) {
    if (uVar4 + 0xc < 0x20) {
      uVar4 = uVar4 + 0xc;
    }
    else {
      uVar4 = 0x1f;
    }
  }
  *DAT_0042b9f0 = *DAT_0042b9f0 & 0xc1ffffff | (uVar4 & 0x1f) << 0x19;
  *DAT_0042b9f8 = *DAT_0042b9f8 & 0xffffe0ff | uVar5 << 8;
  if (((param_2 == 1) || (param_2 == 5)) || (param_2 == 0x11)) {
    *DAT_0042bde4 = *DAT_0042bde4 & 0xc1ffffff | 0x8000000;
  }
  else {
    *DAT_0042bde4 = *DAT_0042bde4 & 0xc1ffffff | 0xc000000;
  }
  *puVar3 = *puVar3 & 0xdfffffff;
  *puVar3 = *puVar3 & 0xefffffff;
  uVar4 = *puVar2;
  *puVar2 = uVar4 - iVar6 & 0x3ff | uVar4 & 0xfffffc00;
  *puVar1 = *puVar1 - iVar7 & 0x3f | *puVar1 & 0xffffffc0;
  return;
}

