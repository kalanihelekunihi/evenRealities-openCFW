
undefined4 FUN_00590104(uint *param_1,byte *param_2)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  uint *puVar7;
  uint uVar8;
  uint uVar9;
  byte *pbVar10;
  byte *pbVar11;
  uint in_fpscr;
  double dVar12;
  longlong lVar13;
  
  iVar2 = DAT_00590814;
  uVar9 = param_1[1];
  if (((param_1 == (uint *)0x0) || (param_2 == (byte *)0x0)) || (1 < param_1[1])) {
    uVar3 = 6;
  }
  else if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00590a20)) {
    uVar3 = 2;
  }
  else if ((int)(*param_1 << 6) < 0) {
    uVar3 = 7;
  }
  else {
    pbVar10 = *(byte **)(param_2 + 0x1c);
    pbVar11 = *(byte **)(param_2 + 0x20);
    if (((*(uint *)(pbVar10 + 4) < 9) && (*(uint *)(pbVar10 + 8) < 9)) &&
       ((*(int *)(pbVar10 + 4) != 0 && ((uint)(*(int *)(pbVar10 + 8) + *(int *)(pbVar10 + 4)) < 9)))
       ) {
      if ((((pbVar10[0x14] == 0) || (pbVar10[0x14] == 2)) || (pbVar10[0x14] == 4)) ||
         (pbVar10[0x14] == 5)) {
        if (((pbVar10[0x15] == 0) || (pbVar10[0x15] == 2)) ||
           ((pbVar10[0x15] == 4 || (pbVar10[0x15] == 5)))) {
          if ((((pbVar10[0xc] == 0) || (pbVar10[0xc] == 2)) || (pbVar10[0xc] == 4)) ||
             (pbVar10[0xc] == 5)) {
            if ((((pbVar10[0xd] == 0) || (pbVar10[0xd] == 2)) || (pbVar10[0xd] == 4)) ||
               (pbVar10[0xd] == 5)) {
              *(undefined4 *)(DAT_00590814 + uVar9 * 0x1000 + 0x48) = 0x22;
              FUN_004807a0(200);
              if ((param_2[1] == 1) || (param_2[1] == 2)) {
                uVar6 = 1;
              }
              else {
                uVar6 = 0;
              }
              if (*pbVar10 == 0) {
                if (*(int *)(pbVar10 + 4) == 1) {
                  uVar8 = *(uint *)(DAT_00590cf0 + (uint)pbVar10[0xc] * 4);
                }
                else {
                  uVar8 = *(int *)(DAT_00590cf0 + (uint)pbVar10[0xc] * 4) * *(int *)(pbVar10 + 4);
                }
              }
              else {
                uVar8 = *(int *)(DAT_00590cf0 + (uint)pbVar10[0xc] * 4) * *(int *)(pbVar10 + 4) +
                        *(int *)(DAT_00590cf0 + (uint)pbVar10[0xd] * 4) * *(int *)(pbVar10 + 8);
              }
              bVar1 = *pbVar11;
              if (bVar1 == 0) {
                uVar4 = *(uint *)(DAT_00590cf0 + (uint)pbVar10[0xc] * 4);
              }
              else if (bVar1 == 2) {
                uVar4 = uVar8 >> 1;
              }
              else if (bVar1 < 2) {
                uVar4 = 1;
              }
              else {
                if (bVar1 != 3) {
                  return 6;
                }
                uVar4 = *(uint *)(pbVar11 + 4);
                if ((uVar4 == 0) || (uVar8 <= uVar4)) {
                  return 6;
                }
              }
              *(uint *)(iVar2 + uVar9 * 0x1000 + 0x44) =
                   (uVar4 - 1) * 0x100000 & 0xff00000 |
                   uVar6 | (uVar8 - 1) * 0x10 & 0xfff0 | (pbVar11[8] & 1) << 0x10 |
                   (pbVar11[10] & 1) << 0x11 | (*param_2 & 1) << 0x12 | (pbVar11[9] & 1) << 0x13;
              *(uint *)(iVar2 + uVar9 * 0x1000 + 0x40) =
                   pbVar10[0x14] & 7 | (pbVar10[0x16] & 1) << 3 | (pbVar10[0xc] & 7) << 5 |
                   (*(int *)(pbVar10 + 4) + -1) * 0x100 & 0x7f00U | (pbVar10[0x15] & 7) << 0x10 |
                   (*(uint *)(pbVar10 + 0x10) & 3) << 0x13 | (pbVar10[0xd] & 7) << 0x15 |
                   (*(int *)(pbVar10 + 8) + -1) * 0x1000000 & 0x7f000000U | (uint)*pbVar10 << 0x1f;
              if ((*param_2 == 1) && (*(int *)(param_2 + 0x18) != 0)) {
                uVar3 = 6;
              }
              else {
                if ((*param_2 == 0) && (*(int *)(param_2 + 0x18) != 0)) {
                  bVar1 = 0;
                }
                else {
                  bVar1 = 1;
                }
                puVar7 = (uint *)(iVar2 + uVar9 * 0x1000 + 0x54);
                *puVar7 = *puVar7 & 0xfffffffd | (uint)bVar1 << 1;
                puVar7 = (uint *)(iVar2 + uVar9 * 0x1000 + 0x54);
                *puVar7 = *puVar7 | 4;
                if ((*param_2 == 1) || ((*param_2 == 0 && (*(int *)(param_2 + 0x18) != 0)))) {
                  *(undefined1 *)(param_1 + 0x18) = 1;
                }
                else {
                  *(undefined1 *)(param_1 + 0x18) = 0;
                }
                if ((char)param_1[0x18] == '\0') {
                  param_1[0x17] = 0x217;
                }
                else {
                  if ((((*DAT_00590d30 & 0xff) == 0x21) && (*(int *)(param_2 + 4) != 0x100)) &&
                     (*(int *)(param_2 + 4) != 0)) {
                    return 6;
                  }
                  iVar5 = FUN_0058fd1c(*(undefined4 *)(param_2 + 4));
                  if (iVar5 == 7) {
                    return 6;
                  }
                  param_1[0x17] = *(uint *)(param_2 + 4);
                  if ((*(uint *)(param_2 + 4) & 0xffffff) >> 0x10 == 1) {
                    uVar6 = (uint)(0.0 < *(double *)(param_2 + 0x10)) *
                            (int)(longlong)*(double *)(param_2 + 0x10);
                    dVar12 = (double)VectorUnsignedToFloat(uVar6,(byte)(in_fpscr >> 0x16) & 3);
                    dVar12 = (*(double *)(param_2 + 0x10) - dVar12) * DAT_00590640 + 0.5;
                    lVar13 = FUN_0059823c(SUB84(dVar12,0),(int)((ulonglong)dVar12 >> 0x20));
                    uVar3 = (undefined4)lVar13;
                    if (lVar13 == 0x100000000) {
                      uVar6 = uVar6 + 1;
                      uVar3 = 0;
                    }
                    if (uVar6 < 4) {
                      return 6;
                    }
                    *(uint *)(iVar2 + uVar9 * 0x1000 + 0x60) = uVar6;
                    *(undefined4 *)(iVar2 + uVar9 * 0x1000 + 100) = uVar3;
                  }
                  puVar7 = (uint *)(iVar2 + uVar9 * 0x1000 + 0x100);
                  *puVar7 = *puVar7 & 0xffefffff | (uint)(*(int *)(param_2 + 8) != 0) << 0x14;
                }
                *(undefined4 *)(iVar2 + uVar9 * 0x1000 + 0x10) = 0x20;
                *(undefined4 *)(iVar2 + uVar9 * 0x1000 + 0x30) = 0x20;
                uVar3 = 0;
              }
            }
            else {
              uVar3 = 6;
            }
          }
          else {
            uVar3 = 6;
          }
        }
        else {
          uVar3 = 6;
        }
      }
      else {
        uVar3 = 6;
      }
    }
    else {
      uVar3 = 6;
    }
  }
  return uVar3;
}

