
int af_latin_hints_compute_segments(undefined4 *param_1,byte param_2)

{
  bool bVar1;
  bool bVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  byte *pbVar8;
  ushort *puVar9;
  ushort *puVar10;
  int iVar11;
  int iVar12;
  ushort uVar13;
  int iVar14;
  byte *local_98;
  byte local_94;
  byte local_93;
  ushort local_92;
  int local_90;
  int local_8c;
  int local_88;
  int local_84;
  int *local_80;
  ushort local_7c;
  ushort local_7a;
  int local_78;
  int local_74;
  undefined4 *local_70;
  int local_6c;
  int local_68;
  uint local_64;
  int local_60;
  ushort *local_5c;
  undefined4 *local_58;
  undefined4 local_54;
  undefined1 local_50 [28];
  undefined4 local_34;
  
  local_80 = param_1 + (uint)param_2 * 0x151 + 0xb;
  local_54 = *param_1;
  local_60 = 0;
  local_98 = (byte *)0x0;
  local_70 = (undefined4 *)param_1[10];
  local_58 = local_70 + param_1[9];
  local_64 = *(uint *)(param_1[0x2af] + 0x28) / 0xe;
  FUN_0043c0e4(local_50,0x2c,0);
  local_34 = 32000;
  local_50[0] = 0;
  if ((char)local_80[6] < '\0') {
    local_94 = -(char)local_80[6];
  }
  else {
    local_94 = *(byte *)(local_80 + 6);
  }
  local_93 = local_94;
  *local_80 = 0;
  if (param_2 == 0) {
    uVar4 = param_1[7];
    uVar3 = uVar4 + param_1[6] * 0x28;
    for (; uVar4 < uVar3; uVar4 = uVar4 + 0x28) {
      *(int *)(uVar4 + 0x18) = (int)*(short *)(uVar4 + 0xc);
      *(int *)(uVar4 + 0x1c) = (int)*(short *)(uVar4 + 0xe);
    }
  }
  else {
    uVar4 = param_1[7];
    uVar3 = uVar4 + param_1[6] * 0x28;
    for (; uVar4 < uVar3; uVar4 = uVar4 + 0x28) {
      *(int *)(uVar4 + 0x18) = (int)*(short *)(uVar4 + 0xe);
      *(int *)(uVar4 + 0x1c) = (int)*(short *)(uVar4 + 0xc);
    }
  }
LAB_005a9aba:
  if (local_58 <= local_70) {
    local_98 = (byte *)local_80[2];
    pbVar8 = local_98 + *local_80 * 0x2c;
    for (; local_98 < pbVar8; local_98 = local_98 + 0x2c) {
      iVar11 = *(int *)(local_98 + 0x24);
      iVar12 = *(int *)(local_98 + 0x28);
      iVar14 = *(int *)(iVar11 + 0x1c);
      iVar5 = *(int *)(iVar12 + 0x1c);
      if (iVar14 < iVar5) {
        if (*(int *)(*(int *)(iVar11 + 0x24) + 0x1c) < iVar14) {
          *(short *)(local_98 + 10) =
               (short)(iVar14 - *(int *)(*(int *)(iVar11 + 0x24) + 0x1c) >> 1) +
               *(short *)(local_98 + 10);
        }
        if (iVar5 < *(int *)(*(int *)(iVar12 + 0x20) + 0x1c)) {
          *(short *)(local_98 + 10) =
               (short)(*(int *)(*(int *)(iVar12 + 0x20) + 0x1c) - iVar5 >> 1) +
               *(short *)(local_98 + 10);
        }
      }
      else {
        if (iVar14 < *(int *)(*(int *)(iVar11 + 0x24) + 0x1c)) {
          *(short *)(local_98 + 10) =
               (short)(*(int *)(*(int *)(iVar11 + 0x24) + 0x1c) - iVar14 >> 1) +
               *(short *)(local_98 + 10);
        }
        if (*(int *)(*(int *)(iVar12 + 0x20) + 0x1c) < iVar5) {
          *(short *)(local_98 + 10) =
               (short)(iVar5 - *(int *)(*(int *)(iVar12 + 0x20) + 0x1c) >> 1) +
               *(short *)(local_98 + 10);
        }
      }
    }
    return local_60;
  }
  puVar9 = (ushort *)*local_70;
  iVar5 = *(int *)(puVar9 + 0x12);
  bVar1 = false;
  iVar11 = 32000;
  local_90 = 32000;
  local_92 = 0;
  uVar13 = 0;
  local_8c = 32000;
  pbVar8 = (byte *)0x0;
  local_84 = 32000;
  local_88 = DAT_005aa3f4;
  local_74 = 32000;
  local_78 = DAT_005aa3f4;
  local_7a = 0;
  local_7c = 0;
  local_68 = 32000;
  local_6c = DAT_005aa3f4;
  if (*(char *)(iVar5 + 3) < '\0') {
    iVar5 = -(int)*(char *)(iVar5 + 3);
  }
  else {
    iVar5 = (int)*(char *)(iVar5 + 3);
  }
  puVar10 = puVar9;
  if (iVar5 == (char)local_94) {
    if ((char)*(byte *)((int)puVar9 + 3) < '\0') {
      iVar5 = -(int)(char)*(byte *)((int)puVar9 + 3);
    }
    else {
      iVar5 = (int)(char)*(byte *)((int)puVar9 + 3);
    }
    if (iVar5 == (char)local_94) {
      do {
        puVar10 = *(ushort **)(puVar10 + 0x12);
        if ((char)*(byte *)((int)puVar10 + 3) < '\0') {
          iVar5 = -(int)(char)*(byte *)((int)puVar10 + 3);
        }
        else {
          iVar5 = (int)(char)*(byte *)((int)puVar10 + 3);
        }
        if (iVar5 != (char)local_94) {
          puVar10 = *(ushort **)(puVar10 + 0x10);
          break;
        }
      } while (puVar10 != puVar9);
    }
  }
  bVar2 = false;
  iVar5 = DAT_005aa3f4;
  iVar12 = DAT_005aa3f4;
  iVar14 = DAT_005aa3f4;
  local_5c = puVar10;
  do {
    if (bVar1) {
      iVar6 = *(int *)(puVar10 + 0xc);
      if (iVar6 < iVar11) {
        iVar11 = iVar6;
      }
      if (iVar5 < iVar6) {
        iVar5 = iVar6;
      }
      iVar6 = *(int *)(puVar10 + 0xe);
      if (iVar6 < local_90) {
        local_92 = *puVar10;
        local_90 = iVar6;
      }
      if (iVar12 < iVar6) {
        uVar13 = *puVar10;
        iVar12 = iVar6;
      }
      if ((*puVar10 & 3) == 0) {
        iVar6 = *(int *)(puVar10 + 0xe);
        if (iVar6 < local_8c) {
          local_8c = iVar6;
        }
        if (iVar14 < iVar6) {
          iVar14 = iVar6;
        }
      }
      if ((*(byte *)((int)puVar10 + 3) != local_93) || (puVar10 == local_5c)) {
        if ((pbVar8 == (byte *)0x0) || (*(int *)(local_98 + 0x24) != *(int *)(pbVar8 + 0x28))) {
          *(ushort **)(local_98 + 0x28) = puVar10;
          *(short *)(local_98 + 2) = (short)(iVar5 + iVar11 >> 1);
          *(short *)(local_98 + 4) = (short)(iVar5 - iVar11 >> 1);
          if ((((local_92 | uVar13) & 3) != 0) && (iVar14 - local_8c < (int)local_64)) {
            *local_98 = *local_98 | 1;
          }
          *(short *)(local_98 + 6) = (short)local_90;
          *(short *)(local_98 + 8) = (short)iVar12;
          *(short *)(local_98 + 10) = *(short *)(local_98 + 8) - *(short *)(local_98 + 6);
          local_74 = local_90;
          local_7a = local_92;
          local_68 = local_8c;
          pbVar8 = local_98;
          local_88 = iVar5;
          local_84 = iVar11;
          local_7c = uVar13;
          local_78 = iVar12;
          local_6c = iVar14;
        }
        else {
          if (*(byte *)(*(int *)(pbVar8 + 0x28) + 2) == (byte)puVar10[1]) {
            if (local_84 < iVar11) {
              iVar11 = local_84;
            }
            if (iVar5 < local_88) {
              iVar5 = local_88;
            }
            if (local_74 < local_90) {
              local_90 = local_74;
              local_92 = local_7a;
            }
            if (iVar12 < local_78) {
              iVar12 = local_78;
              uVar13 = local_7c;
            }
            if (local_68 < local_8c) {
              local_8c = local_68;
            }
            if (iVar14 < local_6c) {
              iVar14 = local_6c;
            }
            *(ushort **)(pbVar8 + 0x28) = puVar10;
            *(short *)(pbVar8 + 2) = (short)(iVar5 + iVar11 >> 1);
            *(short *)(pbVar8 + 4) = (short)(iVar5 - iVar11 >> 1);
            if ((((local_92 | uVar13) & 3) == 0) || ((int)local_64 <= iVar14 - local_8c)) {
              *pbVar8 = *pbVar8 & 0xfe;
            }
            else {
              *pbVar8 = *pbVar8 | 1;
            }
            *(short *)(pbVar8 + 6) = (short)local_90;
            *(short *)(pbVar8 + 8) = (short)iVar12;
            *(short *)(pbVar8 + 10) = *(short *)(pbVar8 + 8) - *(short *)(pbVar8 + 6);
          }
          else {
            if (iVar12 - local_90 < 0) {
              iVar6 = local_90 - iVar12;
            }
            else {
              iVar6 = iVar12 - local_90;
            }
            if (local_78 - local_74 < 0) {
              iVar7 = local_74 - local_78;
            }
            else {
              iVar7 = local_78 - local_74;
            }
            if (iVar6 < iVar7) {
              if (iVar11 < local_84) {
                local_84 = iVar11;
              }
              if (local_88 < iVar5) {
                local_88 = iVar5;
              }
              *(ushort **)(pbVar8 + 0x28) = puVar10;
              *(short *)(pbVar8 + 2) = (short)(local_88 + local_84 >> 1);
              *(short *)(pbVar8 + 4) = (short)(local_88 - local_84 >> 1);
            }
            else {
              if (local_84 < iVar11) {
                iVar11 = local_84;
              }
              if (iVar5 < local_88) {
                iVar5 = local_88;
              }
              *(ushort **)(local_98 + 0x28) = puVar10;
              *(short *)(local_98 + 2) = (short)(iVar5 + iVar11 >> 1);
              *(short *)(local_98 + 4) = (short)(iVar5 - iVar11 >> 1);
              if ((((local_92 | uVar13) & 3) != 0) && (iVar14 - local_8c < (int)local_64)) {
                *local_98 = *local_98 | 1;
              }
              *(short *)(local_98 + 6) = (short)local_90;
              *(short *)(local_98 + 8) = (short)iVar12;
              *(short *)(local_98 + 10) = *(short *)(local_98 + 8) - *(short *)(local_98 + 6);
              FUN_00439c04(pbVar8,local_98,0x2c);
              local_74 = local_90;
              local_7a = local_92;
              local_68 = local_8c;
              local_88 = iVar5;
              local_84 = iVar11;
              local_7c = uVar13;
              local_78 = iVar12;
              local_6c = iVar14;
            }
          }
          *local_80 = *local_80 + -1;
        }
        bVar1 = false;
        local_98 = (byte *)0x0;
      }
    }
    if (puVar10 == local_5c) {
      if (bVar2) break;
      bVar2 = true;
    }
    if (!bVar1) {
      if ((char)*(byte *)((int)puVar10 + 3) < '\0') {
        iVar6 = -(int)(char)*(byte *)((int)puVar10 + 3);
      }
      else {
        iVar6 = (int)(char)*(byte *)((int)puVar10 + 3);
      }
      if ((iVar6 == (char)local_94) || (puVar10 == *(ushort **)(puVar10 + 0x12))) {
        local_93 = *(byte *)((int)puVar10 + 3);
        local_60 = af_axis_hints_new_segment(local_80,local_54,&local_98);
        if (local_60 != 0) {
          return local_60;
        }
        FUN_00439c04(local_98,local_50,0x2c);
        local_98[1] = local_93;
        *(ushort **)(local_98 + 0x24) = puVar10;
        *(ushort **)(local_98 + 0x28) = puVar10;
        if (pbVar8 != (byte *)0x0) {
          pbVar8 = local_98 + -0x2c;
        }
        iVar11 = *(int *)(puVar10 + 0xc);
        iVar12 = *(int *)(puVar10 + 0xe);
        uVar13 = *puVar10;
        if ((*puVar10 & 3) == 0) {
          iVar14 = *(int *)(puVar10 + 0xe);
          local_8c = iVar14;
        }
        else {
          local_8c = 32000;
          iVar14 = DAT_005aa3f4;
        }
        bVar1 = true;
        iVar5 = iVar11;
        local_92 = uVar13;
        local_90 = iVar12;
        if (puVar10 == *(ushort **)(puVar10 + 0x12)) {
          *(short *)(local_98 + 2) = (short)iVar11;
          if ((*puVar10 & 3) != 0) {
            *local_98 = *local_98 | 1;
          }
          *(short *)(local_98 + 6) = (short)*(undefined4 *)(puVar10 + 0xe);
          *(short *)(local_98 + 8) = (short)*(undefined4 *)(puVar10 + 0xe);
          local_98[10] = 0;
          local_98[0xb] = 0;
          bVar1 = false;
          local_98 = (byte *)0x0;
        }
      }
    }
    puVar10 = *(ushort **)(puVar10 + 0x10);
  } while( true );
  local_70 = local_70 + 1;
  goto LAB_005a9aba;
}

