
undefined4 FUN_1000ad60(uint param_1,int param_2,int *param_3,uint *param_4)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  undefined1 *puVar5;
  uint uVar6;
  uint *puVar7;
  undefined1 *puVar8;
  undefined1 *puVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  uint uVar14;
  uint uVar15;
  int iVar16;
  
  iVar16 = DAT_1000af7c;
  iVar10 = DAT_1000af78;
  iVar12 = DAT_1000af78;
  if ((param_1 & 0xff) != 0) {
    if ((param_1 & 0xff) == 1) {
      iVar10 = DAT_1000af80 + -0x17c;
      iVar12 = DAT_1000af80;
    }
    else {
      iVar12 = 0;
    }
  }
  iVar11 = param_1 * 4;
  uVar14 = (uint)*(ushort *)(param_2 + 8) + (uint)(*(char *)(param_2 + 7) != '\0') * -4;
  uVar4 = *(uint *)(iVar10 + iVar11 + 0x308);
  puVar8 = (undefined1 *)*param_3;
  if (uVar14 == uVar4) {
    *(undefined4 *)(iVar10 + iVar11 + 0x308) = 0;
    FUN_100046ac(*(undefined4 *)(iVar12 + 8),PTR_LAB_1000af8c,0);
    if (*(char *)(param_2 + 7) == '\0') {
      *(undefined4 *)(iVar12 + 0x170) = 0;
      *(char *)(iVar12 + 0x30) = (char)param_1;
      *(uint *)(iVar12 + 0x34) =
           (uint)*(ushort *)(iVar12 + 0x24) + (uint)(*(char *)(iVar12 + 0x23) != '\0') * -4;
      FUN_10015b64(DAT_1000af90,iVar12 + 0x1c);
      *(undefined4 *)(iVar12 + 0x1c) = 0;
      *(undefined4 *)(iVar12 + 0x34) = 0;
      uVar2 = 0;
    }
    else {
      *(undefined4 *)(iVar12 + 0x170) = 3;
      uVar2 = 0;
    }
  }
  else {
    puVar5 = puVar8;
    if (uVar4 == 0) {
      if (*(uint *)(DAT_1000af7c + 4) != (uint)*(ushort *)(param_2 + 4)) {
        puVar7 = (uint *)(DAT_1000af7c + 0x20);
        iVar13 = 1;
        iVar3 = 0xf;
        do {
          if (*puVar7 == (uint)*(ushort *)(param_2 + 4)) goto LAB_1000af16;
          iVar13 = iVar13 + 1;
          puVar7 = puVar7 + 7;
          iVar3 = iVar3 + -1;
        } while (iVar3 != 0);
LAB_1000ae4e:
        *(undefined4 *)(param_2 + 0x10) = 0;
        *(undefined4 *)(param_2 + 0x18) = 0;
        return 0xffffffff;
      }
      iVar13 = 0;
LAB_1000af16:
      iVar3 = DAT_1000af7c + iVar13 * 0x1c;
      if (*(uint *)(iVar3 + 0xc) < uVar14) goto LAB_1000ae4e;
      if (*(uint *)(iVar3 + 0xc) < (uint)*(ushort *)(param_2 + 8) + *(int *)(iVar3 + 0x10)) {
        *(undefined4 *)(iVar3 + 0x10) = 0;
      }
      iVar16 = iVar16 + iVar13 * 0x1c;
      if (*(int *)(iVar16 + 8) == 0) goto LAB_1000ae4e;
      iVar13 = *(int *)(iVar16 + 0x10);
      *(int *)(param_2 + 0x10) = *(int *)(iVar16 + 8) + iVar13;
      *(uint *)(iVar16 + 0x10) = iVar13 + uVar14;
      puVar5 = (undefined1 *)*param_3;
    }
    if (((puVar5 == (undefined1 *)0x0) || (param_4 == (uint *)0x0)) ||
       (uVar15 = *param_4, uVar15 == 0)) {
      FUN_100046ac(*(undefined4 *)(iVar12 + 8),PTR_LAB_1000af8c,0);
      uVar2 = 0xffffffff;
    }
    else {
      uVar6 = uVar14 - uVar4;
      iVar16 = (uVar6 < uVar15) * uVar15 + (uVar6 >= uVar15) * uVar15;
      if (iVar16 != 0) {
        puVar5 = puVar8;
        do {
          puVar9 = puVar5 + 1;
          puVar5[(uVar4 - (int)puVar8) + *(int *)(param_2 + 0x10)] = *puVar5;
          puVar5 = puVar9;
        } while (puVar8 + iVar16 != puVar9);
        uVar4 = uVar4 + iVar16;
        *(uint *)(iVar10 + iVar11 + 0x308) = uVar4;
        *param_4 = *param_4 - iVar16;
        if (uVar14 == uVar4) {
          cVar1 = *(char *)(param_2 + 7);
          *param_3 = *param_3 + iVar16;
          *(undefined4 *)(iVar10 + iVar11 + 0x308) = 0;
          if (cVar1 != '\0') {
            *(undefined4 *)(iVar12 + 0x170) = 3;
            return 0;
          }
          return 1;
        }
        uVar6 = uVar14 - uVar4;
      }
      if ((0x20 < uVar6) &&
         (uVar4 = *(uint *)(param_2 + 0x10) + uVar4,
         (*(uint *)(param_2 + 0x10) & 0xfffffff0) + 0x10 < uVar4)) {
        FUN_100046e0(param_1);
        FUN_100047a4(param_1,uVar4,uVar6 & 0xfffffff0,PTR_LAB_1000af84,0);
        *param_4 = 0;
        iVar16 = DAT_1000af88;
        *(uint *)(iVar10 + iVar11 + 0x308) =
             *(int *)(iVar10 + iVar11 + 0x308) + (uVar6 & 0xfffffff0);
        *param_3 = iVar16;
        return 0;
      }
      uVar2 = 0;
    }
  }
  return uVar2;
}

