
int FUN_0055cc1c(uint *param_1,int *param_2)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  undefined4 uVar8;
  uint *puVar9;
  uint uVar10;
  undefined4 uVar11;
  uint uVar12;
  int iVar13;
  uint *puVar14;
  undefined4 *puVar15;
  uint uVar16;
  uint uVar17;
  
  uVar17 = 0;
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0055d278)) {
    iVar4 = 2;
  }
  else if (param_2 == (int *)0x0) {
    iVar4 = 6;
  }
  else if (*(byte *)(param_2 + 5) < 2) {
    iVar5 = param_2[4];
    if (iVar5 == 0) {
      *(undefined1 *)(param_2 + 5) = 0;
    }
    iVar4 = FUN_0055c1e0(param_1,param_2,1);
    if (iVar4 == 0) {
      if ((char)param_1[0x20b] == '\x02') {
        iVar4 = 7;
      }
      else {
        uVar16 = param_1[1];
        uVar6 = param_2[2];
        iVar13 = param_2[3];
        iVar7 = param_2[1];
        cVar1 = (char)param_2[5];
        iVar2 = param_2[8];
        iVar4 = FUN_00480826(param_1[0x218],param_1 + 9,0xffffffff,0,1);
        iVar3 = DAT_0055cf38;
        if ((iVar4 == 0) &&
           (iVar4 = FUN_00480826(param_1[0x218],DAT_0055cf38 + uVar16 * 0x1000 + 0x248,6,4,1),
           iVar4 == 0)) {
          uVar8 = *(undefined4 *)(iVar3 + uVar16 * 0x1000 + 0x200);
          *(undefined4 *)(iVar3 + uVar16 * 0x1000 + 0x200) = 0;
          puVar9 = (uint *)(iVar3 + uVar16 * 0x1000 + 0x218);
          *puVar9 = *puVar9 & 0xfffffffe;
          *(undefined4 *)(iVar3 + uVar16 * 0x1000 + 0x208) = 0xffffffff;
          *(int *)(iVar3 + uVar16 * 0x1000 + 0x2c4) = *param_2;
          if ((char)param_1[2] == '\0') {
            uVar10 = (uint)*(byte *)((int)param_1 + *param_2 + 0x8a0);
          }
          else {
            uVar10 = 0;
          }
          *(uint *)(iVar3 + uVar16 * 0x1000 + 0x124) = uVar10;
          if ((char)param_1[2] == '\0') {
            iVar4 = *param_2;
          }
          else {
            iVar4 = 0;
          }
          uVar11 = FUN_0055bce8(iVar4,cVar1,(char)iVar2 != '\0',iVar4,uVar6,iVar13,iVar7,iVar5);
          *(uint *)(iVar3 + uVar16 * 0x1000 + 0x128) = uVar6 >> 8 | iVar13 << 0x18;
          uVar6 = param_2[4];
          if (cVar1 == '\x01') {
            puVar9 = (uint *)param_2[7];
            *(undefined4 *)(iVar3 + uVar16 * 0x1000 + 0x120) = uVar11;
            while (uVar6 != 0) {
              uVar10 = 0;
              while (((uVar12 = (*(uint *)(iVar3 + uVar16 * 0x1000 + 0x100) & 0xffffff) >> 0x10,
                      uVar12 < 4 && (uVar10 < DAT_0055d27c)) && ((uVar17 == 0 || (uVar6 <= uVar12)))
                     )) {
                FUN_004807a0(1);
                uVar17 = *(uint *)(iVar3 + uVar16 * 0x1000 + 0x204) & 1;
                uVar10 = uVar10 + 1;
              }
              if (uVar12 < 4) break;
              while ((3 < uVar12 && (uVar6 != 0))) {
                uVar10 = *(uint *)(iVar3 + uVar16 * 0x1000 + 0x108);
                uVar12 = uVar12 - 4;
                puVar14 = puVar9;
                if (uVar6 < 4) {
                  do {
                    *(char *)puVar14 = (char)uVar10;
                    uVar10 = uVar10 >> 8;
                    uVar6 = uVar6 - 1;
                    puVar14 = (uint *)((int)puVar14 + 1);
                  } while (uVar6 != 0);
                }
                else {
                  *puVar9 = uVar10;
                  puVar9 = puVar9 + 1;
                  uVar6 = uVar6 - 4;
                }
              }
            }
          }
          else if (cVar1 == '\0') {
            puVar15 = (undefined4 *)param_2[6];
            uVar10 = (*(uint *)(iVar3 + uVar16 * 0x1000 + 0x100) & 0xffff) >> 8;
            while ((3 < uVar10 && (uVar6 != 0))) {
              *(undefined4 *)(iVar3 + uVar16 * 0x1000 + 0x10c) = *puVar15;
              puVar15 = puVar15 + 1;
              uVar10 = uVar10 - 4;
              if (uVar6 < 4) {
                uVar6 = 0;
              }
              else {
                uVar6 = uVar6 - 4;
              }
            }
            *(undefined4 *)(iVar3 + uVar16 * 0x1000 + 0x120) = uVar11;
            while (uVar6 != 0) {
              uVar10 = 0;
              while (((uVar12 = (*(uint *)(iVar3 + uVar16 * 0x1000 + 0x100) & 0xffff) >> 8,
                      uVar12 < 4 &&
                      (uVar17 = *(uint *)(iVar3 + uVar16 * 0x1000 + 0x204) & 1, uVar17 == 0)) &&
                     (uVar10 < DAT_0055d27c))) {
                FUN_004807a0(1);
                uVar10 = uVar10 + 1;
              }
              if ((uVar17 != 0) || (uVar12 < 4)) break;
              while ((3 < uVar12 && (uVar6 != 0))) {
                *(undefined4 *)(iVar3 + uVar16 * 0x1000 + 0x10c) = *puVar15;
                puVar15 = puVar15 + 1;
                uVar12 = uVar12 - 4;
                if (uVar6 < 4) {
                  uVar6 = 0;
                }
                else {
                  uVar6 = uVar6 - 4;
                }
              }
            }
          }
          iVar4 = FUN_00480826(DAT_0055d27c,iVar3 + uVar16 * 0x1000 + 0x248,6,4,1);
          if (((iVar4 == 0) && (iVar4 = FUN_0055bd70(uVar16,0), iVar4 == 0)) && (uVar6 != 0)) {
            iVar4 = 1;
          }
          if (iVar4 != 0) {
            FUN_0055bdac(param_1,*(undefined4 *)(iVar3 + uVar16 * 0x1000 + 0x204));
          }
          *(undefined4 *)(iVar3 + uVar16 * 0x1000 + 0x208) = 0xffffffff;
          *(undefined4 *)(iVar3 + uVar16 * 0x1000 + 0x200) = uVar8;
        }
      }
    }
  }
  else {
    iVar4 = 7;
  }
  return iVar4;
}

