
int af_latin_hints_compute_edges
              (undefined4 *param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  short *psVar5;
  int iVar6;
  short *psVar7;
  short *psVar8;
  byte *pbVar9;
  uint uVar10;
  int iVar11;
  uint uVar12;
  int iVar13;
  undefined1 local_40;
  undefined2 *local_3c;
  undefined4 local_38;
  uint local_34;
  int local_30;
  undefined4 local_2c;
  undefined4 uStack_28;
  
  local_2c = *param_1;
  iVar6 = param_1[0x2af];
  iVar3 = *(int *)(DAT_005aa3f8 + (uint)*(byte *)(*(int *)param_1[0x2af] + 2) * 4);
  local_40 = 0;
  uVar10 = param_1[(uint)param_2 * 0x151 + 0xd];
  local_34 = param_1[(uint)param_2 * 0x151 + 0xb] * 0x2c + uVar10;
  param_1[(uint)param_2 * 0x151 + 0xe] = 0;
  if (param_2 == 0) {
    local_38 = param_1[1];
  }
  else {
    local_38 = param_1[3];
  }
  if (param_2 == 1) {
    local_40 = *(undefined1 *)(iVar3 + 0xc);
  }
  uStack_28 = param_4;
  if (param_2 == 0) {
    iVar3 = FT_DivFix(0x40,param_1[3]);
  }
  else {
    iVar3 = 0;
  }
  local_30 = FT_DivFix(0x20,local_38);
  iVar6 = FT_MulFix(*(undefined4 *)(iVar6 + (uint)param_2 * 0x2430 + 0xf8),local_38);
  if (0x10 < iVar6) {
    iVar6 = 0x10;
  }
  iVar6 = FT_DivFix(iVar6,local_38);
  for (uVar12 = uVar10; uVar12 < local_34; uVar12 = uVar12 + 0x2c) {
    if ((((iVar3 <= *(short *)(uVar12 + 10)) && (*(short *)(uVar12 + 4) <= local_30)) &&
        (*(char *)(uVar12 + 1) != '\x04')) &&
       ((*(int *)(uVar12 + 0x18) == 0 || (iVar3 * 3 <= *(short *)(uVar12 + 10) * 2)))) {
      for (iVar4 = 0; psVar7 = (short *)0x0, iVar4 < (int)param_1[(uint)param_2 * 0x151 + 0xe];
          iVar4 = iVar4 + 1) {
        psVar7 = (short *)(iVar4 * 0x2c + param_1[(uint)param_2 * 0x151 + 0x10]);
        iVar13 = (int)*(short *)(uVar12 + 2) - (int)*psVar7;
        if (iVar13 < 0) {
          iVar13 = -iVar13;
        }
        if ((iVar13 < iVar6) && (*(char *)((int)psVar7 + 0xd) == *(char *)(uVar12 + 1))) break;
      }
      if (psVar7 == (short *)0x0) {
        iVar4 = af_axis_hints_new_edge
                          (param_1 + (uint)param_2 * 0x151 + 0xb,(int)*(short *)(uVar12 + 2),
                           (int)*(char *)(uVar12 + 1),local_40,local_2c,&local_3c);
        if (iVar4 != 0) {
          return iVar4;
        }
        FUN_0043c0e4(local_3c,0x2c,0);
        *(uint *)(local_3c + 0x12) = uVar12;
        *(uint *)(local_3c + 0x14) = uVar12;
        *(undefined1 *)((int)local_3c + 0xd) = *(undefined1 *)(uVar12 + 1);
        *local_3c = *(undefined2 *)(uVar12 + 2);
        uVar2 = FT_MulFix((int)*(short *)(uVar12 + 2),local_38);
        *(undefined4 *)(local_3c + 2) = uVar2;
        *(undefined4 *)(local_3c + 4) = *(undefined4 *)(local_3c + 2);
        *(uint *)(uVar12 + 0x10) = uVar12;
      }
      else {
        *(undefined4 *)(uVar12 + 0x10) = *(undefined4 *)(psVar7 + 0x12);
        *(uint *)(*(int *)(psVar7 + 0x14) + 0x10) = uVar12;
        *(uint *)(psVar7 + 0x14) = uVar12;
      }
    }
  }
  do {
    if (local_34 <= uVar10) {
      psVar5 = (short *)param_1[(uint)param_2 * 0x151 + 0x10];
      psVar8 = psVar5 + param_1[(uint)param_2 * 0x151 + 0xe] * 0x16;
      for (psVar7 = psVar5; psVar7 < psVar8; psVar7 = psVar7 + 0x16) {
        iVar3 = *(int *)(psVar7 + 0x12);
        if (iVar3 != 0) {
          do {
            *(short **)(iVar3 + 0xc) = psVar7;
            iVar3 = *(int *)(iVar3 + 0x10);
          } while (iVar3 != *(int *)(psVar7 + 0x12));
        }
      }
      for (; psVar5 < psVar8; psVar5 = psVar5 + 0x16) {
        iVar3 = 0;
        iVar6 = 0;
        pbVar9 = *(byte **)(psVar5 + 0x12);
        do {
          if ((int)((uint)*pbVar9 << 0x1f) < 0) {
            iVar3 = iVar3 + 1;
          }
          else {
            iVar6 = iVar6 + 1;
          }
          if (((*(int *)(pbVar9 + 0x18) == 0) || (*(int *)(*(int *)(pbVar9 + 0x18) + 0xc) == 0)) ||
             (*(short **)(*(int *)(pbVar9 + 0x18) + 0xc) == psVar5)) {
            bVar1 = false;
          }
          else {
            bVar1 = true;
          }
          if (((*(int *)(pbVar9 + 0x14) != 0) && (*(int *)(*(int *)(pbVar9 + 0x14) + 0xc) != 0)) ||
             (bVar1)) {
            psVar7 = *(short **)(psVar5 + 0xc);
            iVar4 = *(int *)(pbVar9 + 0x14);
            if (bVar1) {
              iVar4 = *(int *)(pbVar9 + 0x18);
              psVar7 = *(short **)(psVar5 + 0xe);
            }
            if (psVar7 == (short *)0x0) {
              psVar7 = *(short **)(iVar4 + 0xc);
            }
            else {
              iVar13 = (int)*psVar5 - (int)*psVar7;
              if (iVar13 < 0) {
                iVar13 = -iVar13;
              }
              iVar11 = (int)*(short *)(pbVar9 + 2) - (int)*(short *)(iVar4 + 2);
              if (iVar11 < 0) {
                iVar11 = -iVar11;
              }
              if (iVar11 < iVar13) {
                psVar7 = *(short **)(iVar4 + 0xc);
              }
            }
            if (bVar1) {
              *(short **)(psVar5 + 0xe) = psVar7;
              *(byte *)(psVar7 + 6) = *(byte *)(psVar7 + 6) | 2;
            }
            else {
              *(short **)(psVar5 + 0xc) = psVar7;
            }
          }
          pbVar9 = *(byte **)(pbVar9 + 0x10);
        } while (pbVar9 != *(byte **)(psVar5 + 0x12));
        *(undefined1 *)(psVar5 + 6) = 0;
        if ((0 < iVar3) && (iVar6 <= iVar3)) {
          *(byte *)(psVar5 + 6) = *(byte *)(psVar5 + 6) | 1;
        }
        if ((*(int *)(psVar5 + 0xe) != 0) && (*(int *)(psVar5 + 0xc) != 0)) {
          psVar5[0xe] = 0;
          psVar5[0xf] = 0;
        }
      }
      return 0;
    }
    if (*(char *)(uVar10 + 1) == '\x04') {
      for (iVar3 = 0; psVar7 = (short *)0x0, iVar3 < (int)param_1[(uint)param_2 * 0x151 + 0xe];
          iVar3 = iVar3 + 1) {
        psVar7 = (short *)(iVar3 * 0x2c + param_1[(uint)param_2 * 0x151 + 0x10]);
        iVar4 = (int)*(short *)(uVar10 + 2) - (int)*psVar7;
        if (iVar4 < 0) {
          iVar4 = -iVar4;
        }
        if (iVar4 < iVar6) break;
      }
      if (psVar7 != (short *)0x0) {
        *(undefined4 *)(uVar10 + 0x10) = *(undefined4 *)(psVar7 + 0x12);
        *(uint *)(*(int *)(psVar7 + 0x14) + 0x10) = uVar10;
        *(uint *)(psVar7 + 0x14) = uVar10;
      }
    }
    uVar10 = uVar10 + 0x2c;
  } while( true );
}

