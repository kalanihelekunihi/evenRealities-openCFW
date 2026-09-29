
undefined8 FUN_005de9d2(int param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  byte *pbVar5;
  int iVar6;
  int iVar7;
  byte *pbVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  byte *pbVar15;
  uint uVar16;
  uint uVar17;
  int local_28;
  
  pbVar5 = (byte *)FUN_005de652(*(int *)(param_1 + 0x10) + 6,param_3);
  local_28 = param_4;
  if (pbVar5 == (byte *)0x0) {
    iVar6 = 0;
  }
  else {
    uVar9 = (uint)pbVar5[3] | (uint)pbVar5[1] << 0x10 | (uint)*pbVar5 << 0x18 | (uint)pbVar5[2] << 8
    ;
    uVar10 = (uint)pbVar5[7] |
             (uint)pbVar5[5] << 0x10 | (uint)pbVar5[4] << 0x18 | (uint)pbVar5[6] << 8;
    if (uVar10 == 0 && uVar9 == 0) {
      iVar6 = 0;
    }
    else if (uVar9 == 0) {
      iVar6 = FUN_005de970(param_1,*(int *)(param_1 + 0x10) + uVar10,param_2);
    }
    else if (uVar10 == 0) {
      iVar6 = FUN_005de8f6(param_1,*(int *)(param_1 + 0x10) + uVar9,param_2);
    }
    else {
      pbVar5 = (byte *)(*(int *)(param_1 + 0x10) + uVar10);
      pbVar15 = (byte *)(*(int *)(param_1 + 0x10) + uVar9);
      uVar12 = (uint)pbVar5[3] |
               (uint)pbVar5[1] << 0x10 | (uint)*pbVar5 << 0x18 | (uint)pbVar5[2] << 8;
      iVar6 = FUN_005de8c2(pbVar15);
      uVar16 = (uint)pbVar15[3] |
               (uint)pbVar15[1] << 0x10 | (uint)*pbVar15 << 0x18 | (uint)pbVar15[2] << 8;
      local_28 = param_1;
      if (uVar12 == 0) {
        iVar6 = FUN_005de8f6(param_1,*(int *)(param_1 + 0x10) + uVar9,param_2);
      }
      else if (iVar6 == 0) {
        iVar6 = FUN_005de970(param_1,*(int *)(param_1 + 0x10) + uVar10,param_2);
      }
      else {
        iVar6 = FUN_005de270(param_1,uVar12 + iVar6 + 1,param_2);
        if (iVar6 == 0) {
          iVar6 = *(int *)(param_1 + 0x20);
          uVar10 = (uint)pbVar15[6] | (uint)pbVar15[5] << 8 | (uint)pbVar15[4] << 0x10;
          uVar11 = (uint)pbVar15[7];
          pbVar15 = pbVar15 + 8;
          uVar9 = 1;
          uVar17 = (uint)pbVar5[6] | (uint)pbVar5[5] << 8 | (uint)pbVar5[4] << 0x10;
          pbVar5 = pbVar5 + 9;
          uVar13 = 1;
          iVar7 = 0;
          while( true ) {
            while (uVar11 + uVar10 < uVar17) {
              for (uVar14 = 0; uVar14 <= uVar11; uVar14 = uVar14 + 1) {
                *(uint *)(iVar6 + iVar7 * 4) = uVar14 + uVar10;
                iVar7 = iVar7 + 1;
              }
              uVar9 = uVar9 + 1;
              if (uVar16 < uVar9) goto LAB_005deb76;
              pbVar8 = pbVar15 + 3;
              uVar10 = (uint)pbVar15[2] | (uint)pbVar15[1] << 8 | (uint)*pbVar15 << 0x10;
              pbVar15 = pbVar15 + 4;
              uVar11 = (uint)*pbVar8;
            }
            if (uVar17 < uVar10) {
              *(uint *)(iVar6 + iVar7 * 4) = uVar17;
              iVar7 = iVar7 + 1;
            }
            uVar13 = uVar13 + 1;
            if (uVar12 < uVar13) break;
            uVar17 = (uint)pbVar5[2] | (uint)pbVar5[1] << 8 | (uint)*pbVar5 << 0x10;
            pbVar5 = pbVar5 + 5;
          }
LAB_005deb76:
          if (uVar12 < uVar13) {
            if (uVar9 <= uVar16) {
              for (uVar12 = 0; uVar12 <= uVar11; uVar12 = uVar12 + 1) {
                *(uint *)(iVar6 + iVar7 * 4) = uVar12 + uVar10;
                iVar7 = iVar7 + 1;
              }
              for (; uVar9 < uVar16; uVar9 = uVar9 + 1) {
                bVar2 = *pbVar15;
                bVar3 = pbVar15[1];
                bVar4 = pbVar15[2];
                bVar1 = pbVar15[3];
                pbVar15 = pbVar15 + 4;
                for (uVar10 = 0; uVar10 <= bVar1; uVar10 = uVar10 + 1) {
                  *(uint *)(iVar6 + iVar7 * 4) =
                       uVar10 + ((uint)bVar4 | (uint)bVar3 << 8 | (uint)bVar2 << 0x10);
                  iVar7 = iVar7 + 1;
                }
              }
            }
          }
          else {
            *(uint *)(iVar6 + iVar7 * 4) = uVar17;
            for (; iVar7 = iVar7 + 1, uVar13 < uVar12; uVar13 = uVar13 + 1) {
              *(uint *)(iVar6 + iVar7 * 4) =
                   (uint)pbVar5[1] << 8 | (uint)*pbVar5 << 0x10 | (uint)pbVar5[2];
              pbVar5 = pbVar5 + 5;
            }
          }
          *(undefined4 *)(iVar6 + iVar7 * 4) = 0;
        }
        else {
          iVar6 = 0;
        }
      }
    }
  }
  return CONCAT44(local_28,iVar6);
}

