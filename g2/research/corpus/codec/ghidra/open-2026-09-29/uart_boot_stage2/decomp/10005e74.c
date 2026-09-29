
undefined4 * FUN_10005e74(int param_1,undefined4 *param_2,int param_3)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  undefined4 *puVar4;
  int iVar5;
  undefined4 *puVar6;
  
  if (param_1 != 0) {
    iVar2 = gx8002_stage2_strchr(param_1,0x2e);
    if (iVar2 == 0) {
      iVar2 = gx8002_stage2_strlen(param_1);
    }
    else {
      iVar2 = iVar2 - param_1;
    }
    puVar1 = param_2 + param_3 * 5;
    if (param_2 != puVar1) {
      iVar5 = 0;
      puVar6 = param_2;
      do {
        while (puVar4 = param_2, iVar3 = FUN_10006294(param_1,*puVar4,iVar2), iVar3 == 0) {
          iVar3 = gx8002_stage2_strlen(*puVar4);
          if (iVar2 == iVar3) {
            return puVar4;
          }
          iVar5 = iVar5 + 1;
          param_2 = puVar4 + 5;
          puVar6 = puVar4;
          if (puVar4 + 5 == puVar1) goto LAB_10005ecc;
        }
        param_2 = puVar4 + 5;
      } while (puVar4 + 5 != puVar1);
LAB_10005ecc:
      if (iVar5 == 1) {
        return puVar6;
      }
    }
  }
  return (undefined4 *)0x0;
}

