
uint FUN_005d9890(int param_1,uint *param_2)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint *puVar6;
  
  uVar1 = 0;
  uVar2 = *param_2 + 1;
  uVar3 = 0;
  uVar5 = *(uint *)(param_1 + 0x10);
  do {
    uVar4 = uVar5;
    if (uVar4 <= uVar3) {
      if ((uVar1 == 0) && (uVar2 = 0, uVar3 < *(uint *)(param_1 + 0x10))) {
        puVar6 = (uint *)(*(int *)(param_1 + 0x14) + uVar3 * 8);
        uVar1 = puVar6[1];
        uVar2 = *puVar6 & 0x7fffffff;
      }
LAB_005d98f0:
      *param_2 = uVar2;
      return uVar1;
    }
    uVar5 = uVar3 + (uVar4 - uVar3 >> 1);
    puVar6 = (uint *)(*(int *)(param_1 + 0x14) + uVar5 * 8);
    if (*puVar6 == uVar2) {
      uVar1 = puVar6[1];
      goto LAB_005d98f0;
    }
    if ((*puVar6 & 0x7fffffff) == uVar2) {
      uVar1 = puVar6[1];
    }
    if ((*puVar6 & 0x7fffffff) < uVar2) {
      uVar3 = uVar5 + 1;
      uVar5 = uVar4;
    }
  } while( true );
}

