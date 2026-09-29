
int FUN_0055cf40(uint *param_1,int *param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  undefined4 uVar7;
  uint *puVar8;
  undefined4 uVar9;
  uint uVar10;
  uint uVar11;
  int iVar12;
  uint uVar13;
  undefined4 *puVar14;
  uint *puVar15;
  uint uVar16;
  uint uVar17;
  uint uVar18;
  int iVar19;
  
  uVar17 = 0;
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0055d278)) {
    iVar4 = 2;
  }
  else if (param_2 == (int *)0x0) {
    iVar4 = 6;
  }
  else if ((char)param_2[5] == '\x02') {
    iVar4 = FUN_0055c1e0(param_1,param_2,1);
    if (iVar4 == 0) {
      if ((char)param_1[0x20b] == '\x02') {
        iVar4 = 7;
      }
      else {
        uVar16 = param_1[1];
        uVar5 = param_2[2];
        iVar12 = param_2[3];
        iVar6 = param_2[1];
        iVar19 = param_2[4];
        iVar1 = param_2[5];
        iVar2 = param_2[8];
        puVar15 = (uint *)param_2[7];
        puVar14 = (undefined4 *)param_2[6];
        iVar4 = FUN_00480826(param_1[0x218],param_1 + 9,0xffffffff,0,1);
        iVar3 = DAT_0055d248;
        if ((iVar4 == 0) &&
           (iVar4 = FUN_00480826(param_1[0x218],DAT_0055d248 + uVar16 * 0x1000 + 0x248,6,4,1),
           iVar4 == 0)) {
          uVar7 = *(undefined4 *)(iVar3 + uVar16 * 0x1000 + 0x200);
          *(undefined4 *)(iVar3 + uVar16 * 0x1000 + 0x200) = 0;
          puVar8 = (uint *)(iVar3 + uVar16 * 0x1000 + 0x218);
          *puVar8 = *puVar8 & 0xfffffffe;
          *(undefined4 *)(iVar3 + uVar16 * 0x1000 + 0x208) = 0xffffffff;
          *(int *)(iVar3 + uVar16 * 0x1000 + 0x2c4) = *param_2;
          puVar8 = (uint *)(iVar3 + uVar16 * 0x1000 + 0x124);
          *puVar8 = *(byte *)((int)param_1 + *param_2 + 0x8a0) & 0xf | *puVar8 & 0xfffffff0;
          puVar8 = (uint *)(iVar3 + uVar16 * 0x1000 + 0x124);
          *puVar8 = *puVar8 | 0x10;
          if ((char)param_1[2] == '\0') {
            iVar4 = *param_2;
          }
          else {
            iVar4 = 0;
          }
          uVar9 = FUN_0055bce8(iVar4,(char)iVar1,(char)iVar2 != '\0',iVar4,uVar5,iVar12,iVar6,iVar19
                              );
          *(uint *)(iVar3 + uVar16 * 0x1000 + 0x128) = uVar5 >> 8 | iVar12 << 0x18;
          *(uint *)(iVar3 + uVar16 * 0x1000 + 0x280) =
               *(uint *)(iVar3 + uVar16 * 0x1000 + 0x280) | 4;
          *(undefined4 *)(iVar3 + uVar16 * 0x1000 + 0x120) = uVar9;
          uVar18 = param_2[4];
          uVar5 = uVar18;
          while ((uVar17 == 0 && (uVar18 != 0 || uVar5 != 0))) {
            uVar10 = *(uint *)(iVar3 + uVar16 * 0x1000 + 0x100);
            uVar13 = *(uint *)(iVar3 + uVar16 * 0x1000 + 0x100);
            uVar11 = 0;
            while( true ) {
              uVar13 = (uVar13 & 0xffffff) >> 0x10;
              uVar10 = (uVar10 & 0xffff) >> 8;
              if ((((3 < uVar10) || (3 < uVar13)) || (DAT_0055d27c <= uVar11)) ||
                 ((uVar17 != 0 && (uVar13 < uVar18)))) break;
              FUN_004807a0(1);
              uVar17 = *(uint *)(iVar3 + uVar16 * 0x1000 + 0x204) & 1;
              uVar10 = *(uint *)(iVar3 + uVar16 * 0x1000 + 0x100);
              uVar13 = *(uint *)(iVar3 + uVar16 * 0x1000 + 0x100);
              uVar11 = uVar11 + 1;
            }
            if ((uVar10 < 4) && (uVar13 < 4)) break;
            while ((3 < uVar10 && (uVar5 != 0))) {
              *(undefined4 *)(iVar3 + uVar16 * 0x1000 + 0x10c) = *puVar14;
              puVar14 = puVar14 + 1;
              uVar10 = uVar10 - 4;
              if (uVar5 < 4) {
                uVar5 = 0;
              }
              else {
                uVar5 = uVar5 - 4;
              }
            }
            while ((3 < uVar13 && (uVar18 != 0))) {
              uVar11 = *(uint *)(iVar3 + uVar16 * 0x1000 + 0x108);
              uVar13 = uVar13 - 4;
              puVar8 = puVar15;
              if (uVar18 < 4) {
                do {
                  *(char *)puVar8 = (char)uVar11;
                  uVar11 = uVar11 >> 8;
                  uVar18 = uVar18 - 1;
                  puVar8 = (uint *)((int)puVar8 + 1);
                } while (uVar18 != 0);
              }
              else {
                *puVar15 = uVar11;
                puVar15 = puVar15 + 1;
                uVar18 = uVar18 - 4;
              }
            }
          }
          iVar4 = FUN_00480826(DAT_0055d27c,iVar3 + uVar16 * 0x1000 + 0x248,6,4,1);
          if (iVar4 == 0) {
            iVar4 = FUN_0055bd70(uVar16,0);
            if (iVar4 == 0) {
              if (uVar18 != 0 || uVar5 != 0) {
                iVar4 = 1;
              }
            }
            else {
              FUN_0055bdac(param_1,*(undefined4 *)(iVar3 + uVar16 * 0x1000 + 0x204));
            }
            *(undefined4 *)(iVar3 + uVar16 * 0x1000 + 0x208) = 0xffffffff;
            *(undefined4 *)(iVar3 + uVar16 * 0x1000 + 0x200) = uVar7;
            puVar15 = (uint *)(iVar3 + uVar16 * 0x1000 + 0x280);
            *puVar15 = *puVar15 & 0xfffffffb;
          }
          else {
            puVar15 = (uint *)(iVar3 + uVar16 * 0x1000 + 0x280);
            *puVar15 = *puVar15 & 0xfffffffb;
          }
        }
      }
    }
  }
  else {
    iVar4 = 7;
  }
  return iVar4;
}

