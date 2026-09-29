
void af_cjk_metrics_init_blues(int *param_1,int param_2)

{
  int iVar1;
  bool bVar2;
  undefined4 uVar3;
  int iVar4;
  int *piVar5;
  int *piVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  short *psVar11;
  char *pcVar12;
  int iVar13;
  int iVar14;
  uint local_1d8;
  short local_1d4;
  short local_1d2;
  int local_1d0;
  int local_1c8;
  int local_1c0 [51];
  int local_f4 [51];
  int local_28;
  
  psVar11 = (short *)(DAT_005a6920 + (uint)*(byte *)(*param_1 + 3) * 4);
  local_28 = param_2;
  uVar3 = af_shaper_buf_create(param_2);
  for (; *psVar11 != 0x1469; psVar11 = psVar11 + 2) {
    pcVar12 = (char *)(DAT_005a6924 + *psVar11);
    if ((int)((uint)*(byte *)(psVar11 + 1) << 0x1e) < 0) {
      iVar1 = 0x2c;
    }
    else {
      iVar1 = 0x1c84;
    }
    uVar9 = 0;
    uVar10 = 0;
    bVar2 = true;
    while (*pcVar12 != '\0') {
      for (; *pcVar12 == ' '; pcVar12 = pcVar12 + 1) {
      }
      if (*pcVar12 == '|') {
        bVar2 = false;
        pcVar12 = pcVar12 + 1;
      }
      else {
        pcVar12 = (char *)af_shaper_get_cluster(pcVar12,param_1,uVar3,&local_1d8);
        if ((local_1d8 < 2) && (iVar4 = af_shaper_get_elem(param_1,uVar3,0,0,0), iVar4 != 0)) {
          iVar4 = FT_Load_Glyph(local_28,iVar4,1);
          FUN_00439c04(&local_1d4,*(int *)(local_28 + 0x54) + 0x6c,0x14);
          if ((iVar4 == 0) && (2 < local_1d2)) {
            iVar4 = -1;
            iVar7 = 0;
            iVar8 = 0;
            for (iVar13 = 0; iVar13 < local_1d4; iVar13 = iVar13 + 1) {
              iVar14 = (int)*(short *)(local_1c8 + iVar13 * 2);
              if (iVar8 < iVar14) {
                if ((int)((uint)*(byte *)(psVar11 + 1) << 0x1e) < 0) {
                  if ((int)((uint)*(byte *)(psVar11 + 1) << 0x1f) < 0) {
                    for (; iVar8 <= iVar14; iVar8 = iVar8 + 1) {
                      if ((iVar4 < 0) || (iVar7 < *(int *)(local_1d0 + iVar8 * 8))) {
                        iVar7 = *(int *)(local_1d0 + iVar8 * 8);
                        iVar4 = iVar8;
                      }
                    }
                  }
                  else {
                    for (; iVar8 <= iVar14; iVar8 = iVar8 + 1) {
                      if ((iVar4 < 0) || (*(int *)(local_1d0 + iVar8 * 8) < iVar7)) {
                        iVar7 = *(int *)(local_1d0 + iVar8 * 8);
                        iVar4 = iVar8;
                      }
                    }
                  }
                }
                else if ((int)((uint)*(byte *)(psVar11 + 1) << 0x1f) < 0) {
                  for (; iVar8 <= iVar14; iVar8 = iVar8 + 1) {
                    if ((iVar4 < 0) || (iVar7 < *(int *)(local_1d0 + iVar8 * 8 + 4))) {
                      iVar7 = *(int *)(local_1d0 + iVar8 * 8 + 4);
                      iVar4 = iVar8;
                    }
                  }
                }
                else {
                  for (; iVar8 <= iVar14; iVar8 = iVar8 + 1) {
                    if ((iVar4 < 0) || (*(int *)(local_1d0 + iVar8 * 8 + 4) < iVar7)) {
                      iVar7 = *(int *)(local_1d0 + iVar8 * 8 + 4);
                      iVar4 = iVar8;
                    }
                  }
                }
              }
              iVar8 = iVar14 + 1;
            }
            if (bVar2) {
              local_f4[uVar9] = iVar7;
              uVar9 = uVar9 + 1;
            }
            else {
              local_1c0[uVar10] = iVar7;
              uVar10 = uVar10 + 1;
            }
          }
        }
      }
    }
    if (uVar9 != 0 || uVar10 != 0) {
      af_sort_pos(uVar9,local_f4);
      af_sort_pos(uVar10,local_1c0);
      iVar4 = *(int *)((int)param_1 + iVar1 + 0xd8) * 0x1c + iVar1;
      piVar5 = (int *)((int)param_1 + iVar4 + 0xdc);
      piVar6 = (int *)((int)param_1 + iVar4 + 0xe8);
      *(int *)((int)param_1 + iVar1 + 0xd8) = *(int *)((int)param_1 + iVar1 + 0xd8) + 1;
      if (uVar10 == 0) {
        *piVar6 = local_f4[uVar9 >> 1];
        *piVar5 = *piVar6;
      }
      else if (uVar9 == 0) {
        *piVar6 = local_1c0[uVar10 >> 1];
        *piVar5 = *piVar6;
      }
      else {
        *piVar5 = local_f4[uVar9 >> 1];
        *piVar6 = local_1c0[uVar10 >> 1];
      }
      if (*piVar6 != *piVar5) {
        if (*piVar6 < *piVar5 != (bool)(*(byte *)(psVar11 + 1) & 1)) {
          *piVar6 = (*piVar5 + *piVar6) / 2;
          *piVar5 = *piVar6;
        }
      }
      *(undefined4 *)((int)param_1 + iVar4 + 0xf4) = 0;
      if ((int)((uint)*(byte *)(psVar11 + 1) << 0x1f) < 0) {
        *(uint *)((int)param_1 + iVar4 + 0xf4) = *(uint *)((int)param_1 + iVar4 + 0xf4) | 2;
      }
    }
  }
  af_shaper_buf_destroy(local_28,uVar3);
  return;
}

