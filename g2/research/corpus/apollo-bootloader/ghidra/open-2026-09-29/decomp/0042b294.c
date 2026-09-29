
int spotmgr_state_transition_42b294(uint param_1,uint param_2,int param_3,int param_4)

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
  
  piVar7 = DAT_0042bdec;
  iVar14 = DAT_0042bd9c;
  puVar6 = DAT_0042b9fc;
  bVar2 = false;
  puVar9 = (uint *)(DAT_0042b6a4 + param_1 * 4 + 4);
  puVar11 = (uint *)(DAT_0042b6a4 + param_2 * 4 + 4);
  puVar13 = (uint *)(DAT_0042b6a4 + *DAT_0042b9fc * 4 + 4);
  bVar16 = false;
  if (param_1 == param_2) {
    if (param_3 != param_4) {
      spotmgr_power_transition_trims_42b06c(param_3,param_1,0);
    }
  }
  else {
    if ((*(uint *)(DAT_0042bd9c + param_2 * 4) < *(uint *)(DAT_0042bd9c + param_1 * 4)) ||
       (*(uint *)(DAT_0042bde8 + param_2 * 4) < *(uint *)(DAT_0042bde8 + param_1 * 4))) {
      bVar2 = true;
    }
    if (bVar2) {
      if ((((((((param_3 != param_4) || (param_1 == 1)) || (param_1 == 5)) ||
             ((param_1 == 0x11 || (param_1 == 8)))) || (param_1 == 0xc)) ||
           (((param_1 == 0xe || (param_1 == 0xf)) ||
            ((param_2 == 1 || (((param_2 == 5 || (param_2 == 0x11)) || (param_2 == 8)))))))) ||
          ((param_2 == 0xc || (param_2 == 0xe)))) || (param_2 == 0xf)) {
        spotmgr_power_transition_trims_42b06c(param_3,param_1);
      }
      puVar4 = DAT_0042b6b4;
      *DAT_0042b6b4 = (*puVar9 & 0xfffffff) >> 0x15;
      puVar5 = DAT_0042b9c4;
      *DAT_0042b9c4 = *(byte *)puVar9 & 0x7f;
      puVar3 = DAT_0042b6a8;
      *DAT_0042b6a8 = *DAT_0042b6a8 & 0xffffc3ff | ((*puVar9 & 0x1fffff) >> 0x11) << 10;
      piVar7 = DAT_0042bdec;
      if (*DAT_0042bdec << 0x1f < 0) {
        if (((*puVar9 & 0x1ffff) >> 7) + 7 < 0x400) {
          *DAT_0042b9bc = 7;
        }
        else {
          *DAT_0042b9bc = 0x3ff - ((*puVar9 & 0x1ffff) >> 7);
        }
        *puVar3 = *DAT_0042b9bc + (*puVar9 >> 7) & 0x3ff | *puVar3 & 0xfffffc00;
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
      if (((iVar14 + uVar8 < 0x80) && (iVar15 + uVar12 < 0x80)) && (*DAT_0042b6ac == '\0')) {
        *DAT_0042b6b0 = *DAT_0042b6b0 & 0xffffff80 | iVar14 + uVar8 & 0x7f;
        *DAT_0042b9c0 = *DAT_0042b9c0 & 0xffffff80 | iVar15 + uVar12 & 0x7f;
        uVar10 = 0x32;
      }
      else {
        *DAT_0042b6b0 = *DAT_0042b6b0 & 0xffffff80 | *puVar4;
        *DAT_0042b9c0 = *DAT_0042b9c0 & 0xffffff80 | *puVar5;
        if (*DAT_0042b6ac == '\0') {
          uVar10 = 200;
        }
        else {
          uVar10 = 2000;
        }
      }
      if (*piVar7 << 0x1f < 0) {
        FUN_0041cc92(uVar10);
      }
      else {
        spotmgr_trim_enable_42adb8(1);
        FUN_0041cc48(uVar10);
        *puVar6 = param_2;
      }
      if (((param_2 < 8) || (param_2 - 0x10 < 4)) && (param_1 - 8 < 8)) {
        bVar16 = *DAT_0042bf50 << 0xe < 0;
        if (bVar16) {
          FUN_0041e22e();
        }
        *DAT_0042b9d0 = *DAT_0042b9d0 | 0x10000;
        *DAT_0042b9c8 = 1;
      }
      delay_us(0x14);
      if (bVar16) {
        FUN_0041e1e8();
      }
    }
    else {
      if ((*DAT_0042bdec << 0x1f < 0) &&
         ((*(uint *)(DAT_0042bd9c + *DAT_0042b9fc * 4) < *(uint *)(DAT_0042bd9c + param_1 * 4) ||
          (*(uint *)(DAT_0042bde8 + *DAT_0042b9fc * 4) < *(uint *)(DAT_0042bde8 + param_1 * 4))))) {
        bVar2 = true;
      }
      else {
        bVar2 = false;
      }
      if (bVar2) {
        if (((*puVar9 & 0x1ffff) >> 7) + 7 < 0x400) {
          *DAT_0042b9bc = 7;
        }
        else {
          *DAT_0042b9bc = 0x3ff - ((*puVar9 & 0x1ffff) >> 7);
        }
        *DAT_0042b6a8 = *DAT_0042b9bc + (*puVar9 >> 7) & 0x3ff | *DAT_0042b6a8 & 0xfffffc00;
      }
      else {
        *DAT_0042b6a8 = (*puVar9 & 0x1ffff) >> 7 | *DAT_0042b6a8 & 0xfffffc00;
      }
      *DAT_0042b6a8 = *DAT_0042b6a8 & 0xffffc3ff | ((*puVar9 & 0x1fffff) >> 0x11) << 10;
      if ((*DAT_0042b6ac == '\0') && (*piVar7 << 0x1f < 0)) {
        *DAT_0042b6b4 = (*puVar9 & 0xfffffff) >> 0x15;
        *DAT_0042b9c4 = *(byte *)puVar9 & 0x7f;
      }
      else {
        *DAT_0042b6b0 = (*puVar9 & 0xfffffff) >> 0x15 | *DAT_0042b6b0 & 0xffffff80;
        *DAT_0042b9c0 = *(byte *)puVar9 & 0x7f | *DAT_0042b9c0 & 0xffffff80;
      }
      if (((((param_3 != param_4) || (param_1 == 1)) || (param_1 == 5)) ||
          (((((param_1 == 0x11 || (param_1 == 8)) ||
             ((param_1 == 0xc || ((param_1 == 0xe || (param_1 == 0xf)))))) || (param_2 == 1)) ||
           (((param_2 == 5 || (param_2 == 0x11)) || (param_2 == 8)))))) ||
         (((param_2 == 0xc || (param_2 == 0xe)) || (param_2 == 0xf)))) {
        spotmgr_power_transition_trims_42b06c(param_3,param_1);
      }
      if ((*piVar7 << 0x1f < 0) &&
         (*(uint *)(iVar14 + param_1 * 4) <= *(uint *)(iVar14 + *puVar6 * 4))) {
        if (*(uint *)(DAT_0042bde8 + param_1 * 4) <= *(uint *)(DAT_0042bde8 + *puVar6 * 4)) {
          FUN_0041ccd6();
          spotmgr_trim_restore_42ae6c();
          spotmgr_profile_trim_42ae24(0);
        }
      }
    }
  }
  return param_4;
}

