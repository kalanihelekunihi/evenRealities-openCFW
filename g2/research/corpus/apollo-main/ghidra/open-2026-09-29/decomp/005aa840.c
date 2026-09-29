
void af_latin_hint_edges(int param_1,byte param_2)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  int iVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  int iVar15;
  int iVar16;
  char local_38;
  
  iVar3 = param_1 + (uint)param_2 * 0x544;
  uVar13 = *(uint *)(iVar3 + 0x40);
  uVar4 = uVar13 + *(int *)(iVar3 + 0x38) * 0x2c;
  uVar10 = 0;
  iVar3 = 0;
  local_38 = '\0';
  uVar9 = uVar13;
  if (param_2 == 1) {
    local_38 = *(char *)(*(int *)(DAT_005ab144 +
                                 (uint)*(byte *)(**(int **)(param_1 + 0xabc) + 2) * 4) + 0xc);
    for (uVar14 = uVar13; uVar14 < uVar4; uVar14 = uVar14 + 0x2c) {
      if (-1 < (int)((uint)*(byte *)(uVar14 + 0xc) << 0x1d)) {
        uVar12 = *(uint *)(uVar14 + 0x18);
        if (((*(int *)(uVar14 + 0x14) != 0) && (uVar12 != 0)) && (*(int *)(uVar12 + 0x14) != 0)) {
          if ((*(byte *)(uVar12 + 0xc) & 8) == 0) {
            if ((*(byte *)(uVar14 + 0xc) & 8) != 0) {
              *(undefined4 *)(uVar14 + 0x14) = 0;
              *(byte *)(uVar14 + 0xc) = *(byte *)(uVar14 + 0xc) & 0xf7;
            }
          }
          else {
            *(undefined4 *)(uVar12 + 0x14) = 0;
            *(byte *)(uVar12 + 0xc) = *(byte *)(uVar12 + 0xc) & 0xf7;
          }
        }
        iVar6 = *(int *)(uVar14 + 0x14);
        uVar8 = uVar14;
        if (((iVar6 == 0) && (uVar8 = 0, uVar12 != 0)) && (*(int *)(uVar12 + 0x14) != 0)) {
          iVar6 = *(int *)(uVar12 + 0x14);
          uVar8 = uVar12;
          uVar12 = uVar14;
        }
        if (uVar8 != 0) {
          *(undefined4 *)(uVar8 + 8) = *(undefined4 *)(iVar6 + 8);
          *(byte *)(uVar8 + 0xc) = *(byte *)(uVar8 + 0xc) | 4;
          if ((uVar12 != 0) && (*(int *)(uVar12 + 0x14) == 0)) {
            af_latin_align_linked_edge(param_1,1,uVar8,uVar12);
            *(byte *)(uVar12 + 0xc) = *(byte *)(uVar12 + 0xc) | 4;
          }
          if (uVar10 == 0) {
            uVar10 = uVar14;
          }
        }
      }
    }
  }
  for (; uVar9 < uVar4; uVar9 = uVar9 + 0x2c) {
    if (-1 < (int)((uint)*(byte *)(uVar9 + 0xc) << 0x1d)) {
      iVar6 = *(int *)(uVar9 + 0x18);
      if (iVar6 == 0) {
        iVar3 = iVar3 + 1;
      }
      else if (*(int *)(iVar6 + 0x14) == 0) {
        if (uVar10 == 0) {
          iVar11 = *(int *)(iVar6 + 4) - *(int *)(uVar9 + 4);
          iVar5 = af_latin_compute_stem_width
                            (param_1,param_2,iVar11,0,*(undefined1 *)(uVar9 + 0xc),
                             *(undefined1 *)(iVar6 + 0xc));
          if (iVar5 < 0x41) {
            iVar15 = 0x20;
            iVar16 = 0x20;
          }
          else {
            iVar15 = 0x26;
            iVar16 = 0x1a;
          }
          if (iVar5 < 0x60) {
            iVar7 = *(int *)(uVar9 + 4) + (iVar11 >> 1);
            uVar10 = iVar7 + 0x20U & 0xffffffc0;
            iVar11 = iVar15 + (iVar7 - uVar10);
            if (iVar11 < 0) {
              iVar11 = -iVar11;
            }
            iVar7 = (iVar7 - uVar10) - iVar16;
            if (iVar7 < 0) {
              iVar7 = -iVar7;
            }
            if (iVar11 < iVar7) {
              iVar16 = -iVar15;
            }
            *(uint *)(uVar9 + 8) = (uVar10 + iVar16) - iVar5 / 2;
            *(int *)(iVar6 + 8) = iVar5 + *(int *)(uVar9 + 8);
          }
          else {
            *(uint *)(uVar9 + 8) = *(int *)(uVar9 + 4) + 0x20U & 0xffffffc0;
          }
          *(byte *)(uVar9 + 0xc) = *(byte *)(uVar9 + 0xc) | 4;
          af_latin_align_linked_edge(param_1,param_2,uVar9,iVar6);
          uVar10 = uVar9;
        }
        else {
          iVar5 = *(int *)(iVar6 + 4) - *(int *)(uVar9 + 4);
          iVar11 = ((*(int *)(uVar9 + 4) + *(int *)(uVar10 + 8)) - *(int *)(uVar10 + 4)) +
                   (iVar5 >> 1);
          iVar5 = af_latin_compute_stem_width
                            (param_1,param_2,iVar5,0,*(undefined1 *)(uVar9 + 0xc),
                             *(undefined1 *)(iVar6 + 0xc));
          if ((int)((uint)*(byte *)(iVar6 + 0xc) << 0x1d) < 0) {
            *(int *)(uVar9 + 8) = *(int *)(iVar6 + 8) - iVar5;
          }
          else if (iVar5 < 0x60) {
            uVar14 = iVar11 + 0x20U & 0xffffffc0;
            if (iVar5 < 0x41) {
              iVar15 = 0x20;
              iVar16 = 0x20;
            }
            else {
              iVar15 = 0x26;
              iVar16 = 0x1a;
            }
            iVar7 = iVar15 + (iVar11 - uVar14);
            if (iVar7 < 0) {
              iVar7 = -iVar7;
            }
            iVar11 = (iVar11 - uVar14) - iVar16;
            if (iVar11 < 0) {
              iVar11 = -iVar11;
            }
            if (iVar7 < iVar11) {
              iVar16 = -iVar15;
            }
            *(uint *)(uVar9 + 8) = (uVar14 + iVar16) - iVar5 / 2;
            *(uint *)(iVar6 + 8) = iVar5 / 2 + uVar14 + iVar16;
          }
          else {
            iVar7 = (*(int *)(uVar9 + 4) + *(int *)(uVar10 + 8)) - *(int *)(uVar10 + 4);
            iVar15 = *(int *)(iVar6 + 4) - *(int *)(uVar9 + 4);
            iVar11 = iVar7 + (iVar15 >> 1);
            iVar16 = af_latin_compute_stem_width
                               (param_1,param_2,iVar15,0,*(undefined1 *)(uVar9 + 0xc),
                                *(undefined1 *)(iVar6 + 0xc));
            uVar14 = iVar7 + 0x20U & 0xffffffc0;
            iVar5 = (uVar14 + (iVar16 >> 1)) - iVar11;
            if (iVar5 < 0) {
              iVar5 = -iVar5;
            }
            uVar12 = (iVar15 + iVar7 + 0x20U & 0xffffffc0) - iVar16;
            iVar11 = (uVar12 + (iVar16 >> 1)) - iVar11;
            if (iVar11 < 0) {
              iVar11 = -iVar11;
            }
            if (iVar11 <= iVar5) {
              uVar14 = uVar12;
            }
            *(uint *)(uVar9 + 8) = uVar14;
            *(int *)(iVar6 + 8) = iVar16 + *(int *)(uVar9 + 8);
          }
          *(byte *)(uVar9 + 0xc) = *(byte *)(uVar9 + 0xc) | 4;
          *(byte *)(iVar6 + 0xc) = *(byte *)(iVar6 + 0xc) | 4;
          if (uVar13 < uVar9) {
            if (local_38 == '\0') {
              if (*(int *)(uVar9 + 8) < *(int *)(uVar9 - 0x24)) {
                bVar1 = true;
              }
              else {
                bVar1 = false;
              }
            }
            else if (*(int *)(uVar9 - 0x24) < *(int *)(uVar9 + 8)) {
              bVar1 = true;
            }
            else {
              bVar1 = false;
            }
            if ((bVar1) && (*(int *)(uVar9 + 0x18) != 0)) {
              if (*(int *)(*(int *)(uVar9 + 0x18) + 8) - *(int *)(uVar9 - 0x24) < 0) {
                iVar6 = *(int *)(uVar9 - 0x24) - *(int *)(*(int *)(uVar9 + 0x18) + 8);
              }
              else {
                iVar6 = *(int *)(*(int *)(uVar9 + 0x18) + 8) - *(int *)(uVar9 - 0x24);
              }
              if (0x10 < iVar6) {
                *(undefined4 *)(uVar9 + 8) = *(undefined4 *)(uVar9 - 0x24);
              }
            }
          }
        }
      }
      else {
        af_latin_align_linked_edge(param_1,param_2,iVar6,uVar9);
        *(byte *)(uVar9 + 0xc) = *(byte *)(uVar9 + 0xc) | 4;
      }
    }
  }
  iVar6 = (int)(uVar4 - uVar13) / 0x2c;
  if ((param_2 == 0) && ((iVar6 == 6 || (iVar6 == 0xc)))) {
    if (iVar6 == 6) {
      iVar11 = uVar13 + 0x58;
      iVar5 = uVar13 + 0xb0;
      uVar9 = uVar13;
    }
    else {
      uVar9 = uVar13 + 0x2c;
      iVar11 = uVar13 + 0xdc;
      iVar5 = uVar13 + 0x18c;
    }
    iVar16 = (*(int *)(iVar11 + 4) - *(int *)(uVar9 + 4)) -
             (*(int *)(iVar5 + 4) - *(int *)(iVar11 + 4));
    if (iVar16 < 0) {
      iVar16 = -iVar16;
    }
    if (iVar16 < 8) {
      iVar11 = *(int *)(uVar9 + 8) + *(int *)(iVar5 + 8) + *(int *)(iVar11 + 8) * -2;
      *(int *)(iVar5 + 8) = *(int *)(iVar5 + 8) - iVar11;
      if (*(int *)(iVar5 + 0x18) != 0) {
        *(int *)(*(int *)(iVar5 + 0x18) + 8) = *(int *)(*(int *)(iVar5 + 0x18) + 8) - iVar11;
      }
      if (iVar6 == 0xc) {
        *(int *)(uVar13 + 0x168) = *(int *)(uVar13 + 0x168) - iVar11;
        *(int *)(uVar13 + 0x1ec) = *(int *)(uVar13 + 0x1ec) - iVar11;
      }
      *(byte *)(iVar5 + 0xc) = *(byte *)(iVar5 + 0xc) | 4;
      if (*(int *)(iVar5 + 0x18) != 0) {
        *(byte *)(*(int *)(iVar5 + 0x18) + 0xc) = *(byte *)(*(int *)(iVar5 + 0x18) + 0xc) | 4;
      }
    }
  }
  uVar9 = uVar13;
  if ((iVar3 != 0) || (uVar10 == 0)) {
    for (; uVar9 < uVar4; uVar9 = uVar9 + 0x2c) {
      if (-1 < (int)((uint)*(byte *)(uVar9 + 0xc) << 0x1d)) {
        iVar3 = 1000;
        if ((*(int *)(uVar9 + 0x1c) != 0) &&
           (iVar3 = *(int *)(*(int *)(uVar9 + 0x1c) + 4) - *(int *)(uVar9 + 4), iVar3 < 0)) {
          iVar3 = -iVar3;
        }
        if (iVar3 < 0x50) {
          af_latin_align_serif_edge(param_1,*(undefined4 *)(uVar9 + 0x1c),uVar9);
        }
        else {
          uVar14 = uVar9;
          if (uVar10 == 0) {
            *(uint *)(uVar9 + 8) = *(int *)(uVar9 + 4) + 0x20U & 0xffffffc0;
            uVar10 = uVar9;
          }
          else {
            do {
              uVar12 = uVar14;
              uVar14 = uVar12 - 0x2c;
              uVar8 = uVar9;
              if (uVar14 < uVar13) break;
            } while (-1 < (int)((uint)*(byte *)(uVar12 - 0x20) << 0x1d));
            do {
              uVar2 = uVar8;
              uVar8 = uVar2 + 0x2c;
              if (uVar4 <= uVar8) break;
            } while (-1 < (int)((uint)*(byte *)(uVar2 + 0x38) << 0x1d));
            if ((((uVar14 < uVar13) || (uVar9 <= uVar14)) || (uVar4 <= uVar8)) || (uVar8 <= uVar9))
            {
              *(uint *)(uVar9 + 8) =
                   ((*(int *)(uVar9 + 4) - *(int *)(uVar10 + 4)) + 0x10U & 0xffffffe0) +
                   *(int *)(uVar10 + 8);
            }
            else if (*(int *)(uVar2 + 0x30) == *(int *)(uVar12 - 0x28)) {
              *(undefined4 *)(uVar9 + 8) = *(undefined4 *)(uVar12 - 0x24);
            }
            else {
              iVar3 = FT_MulDiv(*(int *)(uVar9 + 4) - *(int *)(uVar12 - 0x28),
                                *(int *)(uVar2 + 0x34) - *(int *)(uVar12 - 0x24),
                                *(int *)(uVar2 + 0x30) - *(int *)(uVar12 - 0x28));
              *(int *)(uVar9 + 8) = iVar3 + *(int *)(uVar12 - 0x24);
            }
          }
        }
        *(byte *)(uVar9 + 0xc) = *(byte *)(uVar9 + 0xc) | 4;
        if (uVar13 < uVar9) {
          if (local_38 == '\0') {
            if (*(int *)(uVar9 + 8) < *(int *)(uVar9 - 0x24)) {
              bVar1 = true;
            }
            else {
              bVar1 = false;
            }
          }
          else if (*(int *)(uVar9 - 0x24) < *(int *)(uVar9 + 8)) {
            bVar1 = true;
          }
          else {
            bVar1 = false;
          }
          if ((bVar1) && (*(int *)(uVar9 + 0x18) != 0)) {
            if (*(int *)(*(int *)(uVar9 + 0x18) + 8) - *(int *)(uVar9 - 0x24) < 0) {
              iVar3 = *(int *)(uVar9 - 0x24) - *(int *)(*(int *)(uVar9 + 0x18) + 8);
            }
            else {
              iVar3 = *(int *)(*(int *)(uVar9 + 0x18) + 8) - *(int *)(uVar9 - 0x24);
            }
            if (0x10 < iVar3) {
              *(undefined4 *)(uVar9 + 8) = *(undefined4 *)(uVar9 - 0x24);
            }
          }
        }
        if ((uVar9 + 0x2c < uVar4) && ((int)((uint)*(byte *)(uVar9 + 0x38) << 0x1d) < 0)) {
          if (local_38 == '\0') {
            if (*(int *)(uVar9 + 0x34) < *(int *)(uVar9 + 8)) {
              bVar1 = true;
            }
            else {
              bVar1 = false;
            }
          }
          else if (*(int *)(uVar9 + 8) < *(int *)(uVar9 + 0x34)) {
            bVar1 = true;
          }
          else {
            bVar1 = false;
          }
          if ((bVar1) && (*(int *)(uVar9 + 0x18) != 0)) {
            if (*(int *)(*(int *)(uVar9 + 0x18) + 8) - *(int *)(uVar9 - 0x24) < 0) {
              iVar3 = *(int *)(uVar9 - 0x24) - *(int *)(*(int *)(uVar9 + 0x18) + 8);
            }
            else {
              iVar3 = *(int *)(*(int *)(uVar9 + 0x18) + 8) - *(int *)(uVar9 - 0x24);
            }
            if (0x10 < iVar3) {
              *(undefined4 *)(uVar9 + 8) = *(undefined4 *)(uVar9 + 0x34);
            }
          }
        }
      }
    }
  }
  return;
}

