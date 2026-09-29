
undefined4 FUN_005dca46(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  undefined1 *puVar6;
  int iVar7;
  uint uVar8;
  
  iVar7 = *param_1;
  iVar1 = *(int *)(iVar7 + 0x1fc);
  iVar3 = *(int *)(iVar7 + 0x200);
  if ((uint)param_1[6] < 0xffff) {
    uVar8 = param_1[6] + 1;
    if (uVar8 < (uint)param_1[10]) {
      uVar8 = param_1[10];
    }
LAB_005dca78:
    uVar4 = param_1[0xb];
    iVar5 = param_1[0xc];
    if (uVar8 <= uVar4) {
      if (param_1[0xd] == 0) {
        do {
          uVar2 = iVar5 + uVar8 & 0xffff;
          if (*(uint *)(iVar7 + 0x10) <= uVar2) {
            uVar2 = 0;
            if (((int)(iVar5 + uVar8) < 0) && (-1 < (int)(iVar5 + uVar4))) {
              uVar8 = -iVar5;
            }
            else {
              if ((0xffff < (int)(iVar5 + uVar8)) || ((int)(iVar5 + uVar4) < 0x10000)) break;
              uVar8 = 0x10000 - iVar5;
            }
          }
          if (uVar2 != 0) {
            param_1[6] = uVar8;
            param_1[7] = uVar2;
            return param_4;
          }
          uVar8 = uVar8 + 1;
        } while (uVar8 <= uVar4);
      }
      else {
        puVar6 = (undefined1 *)(param_1[0xd] + (uVar8 - param_1[10]) * 2);
        if (puVar6 <= (undefined1 *)(iVar1 + iVar3)) {
          do {
            if ((CONCAT11(*puVar6,puVar6[1]) != 0) &&
               (uVar2 = iVar5 + (uint)CONCAT11(*puVar6,puVar6[1]) & 0xffff, uVar2 != 0)) {
              param_1[6] = uVar8;
              param_1[7] = uVar2;
              return param_4;
            }
            uVar8 = uVar8 + 1;
            puVar6 = puVar6 + 2;
          } while (uVar8 <= uVar4);
        }
      }
    }
    iVar5 = FUN_005dc99c(param_1,param_1[9] + 1);
    if (-1 < iVar5) {
      if (uVar8 < (uint)param_1[10]) {
        uVar8 = param_1[10];
      }
      goto LAB_005dca78;
    }
  }
  param_1[6] = -1;
  param_1[7] = 0;
  return param_4;
}

