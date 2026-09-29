
int af_cjk_hints_compute_edges
              (undefined4 *param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  short *psVar7;
  short *psVar8;
  byte *pbVar9;
  uint uVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  short *psVar15;
  undefined2 *local_38;
  undefined4 local_34;
  uint local_30;
  undefined4 local_2c;
  undefined4 uStack_28;
  
  local_2c = *param_1;
  iVar6 = param_1[0x2af] + (uint)param_2 * 0x1c58;
  uVar10 = param_1[(uint)param_2 * 0x151 + 0xd];
  local_30 = uVar10 + param_1[(uint)param_2 * 0x151 + 0xb] * 0x2c;
  param_1[(uint)param_2 * 0x151 + 0xe] = 0;
  if (param_2 == 0) {
    local_34 = param_1[1];
  }
  else {
    local_34 = param_1[3];
  }
  uStack_28 = param_4;
  iVar2 = FT_MulFix(*(undefined4 *)(iVar6 + 0xf8),local_34);
  if (iVar2 < 0x11) {
    iVar6 = *(int *)(iVar6 + 0xf8);
  }
  else {
    iVar6 = FT_DivFix(0x10,local_34);
  }
  do {
    if (local_30 <= uVar10) {
      psVar15 = (short *)param_1[(uint)param_2 * 0x151 + 0x10];
      psVar8 = psVar15 + param_1[(uint)param_2 * 0x151 + 0xe] * 0x16;
      for (psVar7 = psVar15; psVar7 < psVar8; psVar7 = psVar7 + 0x16) {
        iVar6 = *(int *)(psVar7 + 0x12);
        if (iVar6 != 0) {
          do {
            *(short **)(iVar6 + 0xc) = psVar7;
            iVar6 = *(int *)(iVar6 + 0x10);
          } while (iVar6 != *(int *)(psVar7 + 0x12));
        }
      }
      for (; psVar15 < psVar8; psVar15 = psVar15 + 0x16) {
        iVar6 = 0;
        iVar2 = 0;
        pbVar9 = *(byte **)(psVar15 + 0x12);
        do {
          if ((int)((uint)*pbVar9 << 0x1f) < 0) {
            iVar6 = iVar6 + 1;
          }
          else {
            iVar2 = iVar2 + 1;
          }
          if ((*(int *)(pbVar9 + 0x18) == 0) ||
             (*(short **)(*(int *)(pbVar9 + 0x18) + 0xc) == psVar15)) {
            bVar1 = false;
          }
          else {
            bVar1 = true;
          }
          if ((*(int *)(pbVar9 + 0x14) != 0) || (bVar1)) {
            psVar7 = *(short **)(psVar15 + 0xc);
            iVar14 = *(int *)(pbVar9 + 0x14);
            if (bVar1) {
              iVar14 = *(int *)(pbVar9 + 0x18);
              psVar7 = *(short **)(psVar15 + 0xe);
            }
            if (psVar7 == (short *)0x0) {
              psVar7 = *(short **)(iVar14 + 0xc);
            }
            else {
              iVar11 = (int)*psVar15 - (int)*psVar7;
              if (iVar11 < 0) {
                iVar11 = -iVar11;
              }
              if (*(short *)(iVar14 + 2) < *(short *)(pbVar9 + 2)) {
                iVar5 = (int)*(short *)(pbVar9 + 2) - (int)*(short *)(iVar14 + 2);
              }
              else {
                iVar5 = (int)*(short *)(iVar14 + 2) - (int)*(short *)(pbVar9 + 2);
              }
              if (iVar5 < iVar11) {
                psVar7 = *(short **)(iVar14 + 0xc);
              }
            }
            if (bVar1) {
              *(short **)(psVar15 + 0xe) = psVar7;
              *(byte *)(psVar7 + 6) = *(byte *)(psVar7 + 6) | 2;
            }
            else {
              *(short **)(psVar15 + 0xc) = psVar7;
            }
          }
          pbVar9 = *(byte **)(pbVar9 + 0x10);
        } while (pbVar9 != *(byte **)(psVar15 + 0x12));
        *(undefined1 *)(psVar15 + 6) = 0;
        if ((0 < iVar6) && (iVar2 <= iVar6)) {
          *(byte *)(psVar15 + 6) = *(byte *)(psVar15 + 6) | 1;
        }
        if ((*(int *)(psVar15 + 0xe) != 0) && (*(int *)(psVar15 + 0xc) != 0)) {
          psVar15[0xe] = 0;
          psVar15[0xf] = 0;
        }
      }
      return 0;
    }
    psVar7 = (short *)0x0;
    iVar2 = 0xffff;
    for (iVar14 = 0; iVar14 < (int)param_1[(uint)param_2 * 0x151 + 0xe]; iVar14 = iVar14 + 1) {
      psVar15 = (short *)(param_1[(uint)param_2 * 0x151 + 0x10] + iVar14 * 0x2c);
      if (*(char *)((int)psVar15 + 0xd) == *(char *)(uVar10 + 1)) {
        iVar11 = (int)*(short *)(uVar10 + 2) - (int)*psVar15;
        if (iVar11 < 0) {
          iVar11 = -iVar11;
        }
        if ((iVar11 < iVar6) && (iVar11 < iVar2)) {
          iVar5 = *(int *)(uVar10 + 0x14);
          if (iVar5 != 0) {
            iVar12 = *(int *)(psVar15 + 0x12);
            iVar13 = 0;
            do {
              iVar4 = *(int *)(iVar12 + 0x14);
              if (iVar4 != 0) {
                if (*(short *)(iVar4 + 2) < *(short *)(iVar5 + 2)) {
                  iVar13 = (int)*(short *)(iVar5 + 2) - (int)*(short *)(iVar4 + 2);
                }
                else {
                  iVar13 = (int)*(short *)(iVar4 + 2) - (int)*(short *)(iVar5 + 2);
                }
                if (iVar6 <= iVar13) break;
              }
              iVar12 = *(int *)(iVar12 + 0x10);
            } while (iVar12 != *(int *)(psVar15 + 0x12));
            if (iVar6 <= iVar13) goto LAB_005a6dea;
          }
          psVar7 = psVar15;
          iVar2 = iVar11;
        }
      }
LAB_005a6dea:
    }
    if (psVar7 == (short *)0x0) {
      iVar2 = af_axis_hints_new_edge
                        (param_1 + (uint)param_2 * 0x151 + 0xb,(int)*(short *)(uVar10 + 2),
                         (int)*(char *)(uVar10 + 1),0,local_2c,&local_38);
      if (iVar2 != 0) {
        return iVar2;
      }
      FUN_0043c0e4(local_38,0x2c,0);
      *(uint *)(local_38 + 0x12) = uVar10;
      *(uint *)(local_38 + 0x14) = uVar10;
      *(undefined1 *)((int)local_38 + 0xd) = *(undefined1 *)(uVar10 + 1);
      *local_38 = *(undefined2 *)(uVar10 + 2);
      uVar3 = FT_MulFix((int)*(short *)(uVar10 + 2),local_34);
      *(undefined4 *)(local_38 + 2) = uVar3;
      *(undefined4 *)(local_38 + 4) = *(undefined4 *)(local_38 + 2);
      *(uint *)(uVar10 + 0x10) = uVar10;
    }
    else {
      *(undefined4 *)(uVar10 + 0x10) = *(undefined4 *)(psVar7 + 0x12);
      *(uint *)(*(int *)(psVar7 + 0x14) + 0x10) = uVar10;
      *(uint *)(psVar7 + 0x14) = uVar10;
    }
    uVar10 = uVar10 + 0x2c;
  } while( true );
}

