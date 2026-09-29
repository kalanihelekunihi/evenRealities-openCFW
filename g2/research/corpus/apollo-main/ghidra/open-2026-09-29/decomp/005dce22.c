
uint FUN_005dce22(int *param_1,uint *param_2,char param_3)

{
  ushort uVar1;
  int iVar2;
  undefined1 *puVar3;
  uint uVar4;
  uint uVar5;
  undefined1 *puVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  int iVar12;
  undefined1 *puVar13;
  uint uVar14;
  undefined1 *puVar15;
  
  iVar2 = *param_1;
  puVar3 = (undefined1 *)(*(int *)(iVar2 + 0x1fc) + *(int *)(iVar2 + 0x200));
  uVar8 = *param_2;
  uVar4 = 0;
  uVar1 = CONCAT11(*(undefined1 *)(param_1[4] + 6),*(undefined1 *)(param_1[4] + 7));
  uVar7 = uVar1 & 0xfffffffe;
  uVar5 = (uint)(uVar1 >> 1);
  if (uVar5 == 0) {
    uVar4 = 0;
  }
  else {
    if (param_3 != '\0') {
      uVar8 = uVar8 + 1;
    }
    if (uVar8 < 0x10000) {
      puVar6 = (undefined1 *)(param_1[4] + 0xe);
      puVar13 = (undefined1 *)(param_1[4] + uVar7 + 0x10);
      for (uVar14 = 0; uVar14 < uVar5; uVar14 = uVar14 + 1) {
        uVar10 = (uint)CONCAT11(*puVar6,puVar6[1]);
        puVar15 = puVar13 + 2;
        uVar9 = (uint)CONCAT11(*puVar13,puVar13[1]);
        uVar11 = uVar8;
        if ((uVar8 < uVar9) && (uVar11 = uVar9, param_3 == '\0')) break;
        for (; uVar11 <= uVar10; uVar11 = uVar11 + 1) {
          iVar12 = (int)CONCAT11(puVar15[uVar7 - 2],puVar15[uVar7 - 1]);
          puVar13 = puVar15 + (uVar7 - 2) + uVar7;
          uVar8 = (uint)CONCAT11(*puVar13,puVar13[1]);
          if ((((uVar5 - 1 <= uVar14) && (uVar9 == 0xffff)) && (uVar10 == 0xffff)) &&
             ((uVar8 != 0 && (puVar3 < puVar13 + uVar8 + 2)))) {
            iVar12 = 1;
            uVar8 = 0;
          }
          if (uVar8 == 0xffff) break;
          if (uVar8 == 0) {
            uVar4 = iVar12 + uVar11 & 0xffff;
            if ((param_3 != '\0') && (*(uint *)(iVar2 + 0x10) <= uVar4)) {
              uVar4 = 0;
              if (((int)(iVar12 + uVar11) < 0) && (-1 < (int)(iVar12 + uVar10))) {
                uVar11 = -iVar12;
              }
              else {
                if ((0xffff < (int)(iVar12 + uVar11)) || ((int)(iVar12 + uVar10) < 0x10000)) break;
                uVar11 = 0x10000 - iVar12;
              }
            }
          }
          else {
            puVar13 = puVar13 + uVar8 + (uVar11 - uVar9) * 2;
            if ((param_3 != '\0') && (puVar3 < puVar13)) break;
            uVar4 = 0;
            if ((CONCAT11(*puVar13,puVar13[1]) != 0) &&
               (uVar4 = iVar12 + (uint)CONCAT11(*puVar13,puVar13[1]) & 0xffff,
               *(uint *)(iVar2 + 0x10) <= uVar4)) {
              uVar4 = 0;
            }
          }
          uVar8 = uVar11;
          if (((param_3 == '\0') || (uVar4 != 0)) || (0xfffe < uVar11)) goto LAB_005dcfe6;
        }
        puVar6 = puVar6 + 2;
        uVar8 = uVar11;
        puVar13 = puVar15;
      }
LAB_005dcfe6:
      if (param_3 != '\0') {
        *param_2 = uVar8;
      }
    }
    else {
      uVar4 = 0;
    }
  }
  return uVar4;
}

