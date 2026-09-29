
int FUN_005a0fc4(uint param_1,uint param_2,int param_3,int param_4)

{
  byte bVar1;
  bool bVar2;
  uint *puVar3;
  uint *puVar4;
  uint *puVar5;
  uint *puVar6;
  int *piVar7;
  uint uVar8;
  uint *puVar9;
  undefined4 uVar10;
  uint *puVar11;
  uint uVar12;
  uint *puVar13;
  int iVar14;
  int iVar15;
  bool bVar16;
  
  piVar7 = DAT_005a1bb8;
  iVar14 = DAT_005a1734;
  puVar6 = DAT_005a1730;
  bVar2 = false;
  puVar9 = (uint *)(DAT_005a13d4 + param_1 * 4 + 4);
  puVar11 = (uint *)(DAT_005a13d4 + param_2 * 4 + 4);
  puVar13 = (uint *)(DAT_005a13d4 + *DAT_005a1730 * 4 + 4);
  bVar16 = false;
  if (param_1 == param_2) {
    if (param_3 != param_4) {
      FUN_005a0d9c(param_3,param_1,0);
    }
  }
  else {
    if ((*(uint *)(DAT_005a1734 + param_2 * 4) < *(uint *)(DAT_005a1734 + param_1 * 4)) ||
       (*(uint *)(DAT_005a1be8 + param_2 * 4) < *(uint *)(DAT_005a1be8 + param_1 * 4))) {
      bVar2 = true;
    }
    if (bVar2) {
      if ((((((((param_3 != param_4) || (param_1 == 1)) || (param_1 == 5)) ||
             ((param_1 == 0x11 || (param_1 == 8)))) || (param_1 == 0xc)) ||
           (((param_1 == 0xe || (param_1 == 0xf)) ||
            ((param_2 == 1 || (((param_2 == 5 || (param_2 == 0x11)) || (param_2 == 8)))))))) ||
          ((param_2 == 0xc || (param_2 == 0xe)))) || (param_2 == 0xf)) {
        FUN_005a0d9c(param_3,param_1);
      }
      puVar4 = DAT_005a13e4;
      *DAT_005a13e4 = (*puVar9 & 0xfffffff) >> 0x15;
      puVar5 = DAT_005a16f4;
      *DAT_005a16f4 = *(byte *)puVar9 & 0x7f;
      puVar3 = DAT_005a13d8;
      *DAT_005a13d8 = *DAT_005a13d8 & 0xffffc3ff | ((*puVar9 & 0x1fffff) >> 0x11) << 10;
      piVar7 = DAT_005a1bb8;
      if (*DAT_005a1bb8 << 0x1f < 0) {
        if (((*puVar9 & 0x1ffff) >> 7) + 7 < 0x400) {
          *DAT_005a16ec = 7;
        }
        else {
          *DAT_005a16ec = 0x3ff - ((*puVar9 & 0x1ffff) >> 7);
        }
        *puVar3 = *DAT_005a16ec + (*puVar9 >> 7) & 0x3ff | *puVar3 & 0xfffffc00;
        uVar8 = *puVar13;
        bVar1 = *(byte *)puVar13;
      }
      else {
        *puVar3 = (*puVar9 & 0x1ffff) >> 7 | *puVar3 & 0xfffffc00;
        uVar8 = *puVar11;
        bVar1 = *(byte *)puVar11;
      }
      uVar8 = (uVar8 & 0xfffffff) >> 0x15;
      uVar12 = bVar1 & 0x7f;
      if (uVar8 < *puVar4) {
        iVar14 = (*puVar4 - uVar8) * 2;
      }
      else {
        iVar14 = -(uVar8 - *puVar4);
      }
      if (uVar12 < *puVar5) {
        iVar15 = (*puVar5 - uVar12) * 2;
      }
      else {
        iVar15 = -(uVar12 - *puVar5);
      }
      if (((iVar14 + uVar8 < 0x80) && (iVar15 + uVar12 < 0x80)) && (*DAT_005a13dc == '\0')) {
        *DAT_005a13e0 = *DAT_005a13e0 & 0xffffff80 | iVar14 + uVar8 & 0x7f;
        *DAT_005a16f0 = *DAT_005a16f0 & 0xffffff80 | iVar15 + uVar12 & 0x7f;
        uVar10 = 0x32;
      }
      else {
        *DAT_005a13e0 = *DAT_005a13e0 & 0xffffff80 | *puVar4;
        *DAT_005a16f0 = *DAT_005a16f0 & 0xffffff80 | *puVar5;
        if (*DAT_005a13dc == '\0') {
          uVar10 = 200;
        }
        else {
          uVar10 = 2000;
        }
      }
      if (*piVar7 << 0x1f < 0) {
        FUN_0048028a(uVar10);
      }
      else {
        FUN_005a0ae8(1);
        FUN_00480240(uVar10);
        *puVar6 = param_2;
      }
      if (((param_2 < 8) || (param_2 - 0x10 < 4)) && (param_1 - 8 < 8)) {
        bVar16 = *DAT_005a1c14 << 0xe < 0;
        if (bVar16) {
          FUN_00474efa();
        }
        *DAT_005a1700 = *DAT_005a1700 | 0x10000;
        *DAT_005a16f8 = 1;
      }
      FUN_004807a0(0x14);
      if (bVar16) {
        FUN_00474eb4();
      }
    }
    else {
      if ((*DAT_005a1bb8 << 0x1f < 0) &&
         ((*(uint *)(DAT_005a1734 + *DAT_005a1730 * 4) < *(uint *)(DAT_005a1734 + param_1 * 4) ||
          (*(uint *)(DAT_005a1be8 + *DAT_005a1730 * 4) < *(uint *)(DAT_005a1be8 + param_1 * 4))))) {
        bVar2 = true;
      }
      else {
        bVar2 = false;
      }
      if (bVar2) {
        if (((*puVar9 & 0x1ffff) >> 7) + 7 < 0x400) {
          *DAT_005a16ec = 7;
        }
        else {
          *DAT_005a16ec = 0x3ff - ((*puVar9 & 0x1ffff) >> 7);
        }
        *DAT_005a13d8 = *DAT_005a16ec + (*puVar9 >> 7) & 0x3ff | *DAT_005a13d8 & 0xfffffc00;
      }
      else {
        *DAT_005a13d8 = (*puVar9 & 0x1ffff) >> 7 | *DAT_005a13d8 & 0xfffffc00;
      }
      *DAT_005a13d8 = *DAT_005a13d8 & 0xffffc3ff | ((*puVar9 & 0x1fffff) >> 0x11) << 10;
      if ((*DAT_005a13dc == '\0') && (*piVar7 << 0x1f < 0)) {
        *DAT_005a13e4 = (*puVar9 & 0xfffffff) >> 0x15;
        *DAT_005a16f4 = *(byte *)puVar9 & 0x7f;
      }
      else {
        *DAT_005a13e0 = (*puVar9 & 0xfffffff) >> 0x15 | *DAT_005a13e0 & 0xffffff80;
        *DAT_005a16f0 = *(byte *)puVar9 & 0x7f | *DAT_005a16f0 & 0xffffff80;
      }
      if (((((param_3 != param_4) || (param_1 == 1)) || (param_1 == 5)) ||
          (((((param_1 == 0x11 || (param_1 == 8)) ||
             ((param_1 == 0xc || ((param_1 == 0xe || (param_1 == 0xf)))))) || (param_2 == 1)) ||
           (((param_2 == 5 || (param_2 == 0x11)) || (param_2 == 8)))))) ||
         (((param_2 == 0xc || (param_2 == 0xe)) || (param_2 == 0xf)))) {
        FUN_005a0d9c(param_3,param_1);
      }
      if ((*piVar7 << 0x1f < 0) &&
         (*(uint *)(iVar14 + param_1 * 4) <= *(uint *)(iVar14 + *puVar6 * 4))) {
        if (*(uint *)(DAT_005a1be8 + param_1 * 4) <= *(uint *)(DAT_005a1be8 + *puVar6 * 4)) {
          FUN_004802ce();
          FUN_005a0b9c();
          FUN_005a0b54(0);
        }
      }
    }
  }
  return param_4;
}

