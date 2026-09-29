
uint FUN_005d9840(int param_1,uint param_2)

{
  uint *puVar1;
  uint uVar2;
  uint *puVar3;
  uint *puVar4;
  uint *puVar5;
  uint *puVar6;
  
  puVar3 = (uint *)0x0;
  puVar5 = *(uint **)(param_1 + 0x14);
  puVar1 = puVar5 + *(int *)(param_1 + 0x10) * 2 + -2;
  while ((puVar4 = puVar3, puVar5 <= puVar1 &&
         (puVar6 = puVar5 + ((int)puVar1 - (int)puVar5 >> 4) * 2, puVar4 = puVar6,
         *puVar6 != param_2))) {
    if ((*puVar6 & 0x7fffffff) == param_2) {
      puVar3 = puVar6;
    }
    puVar4 = puVar3;
    if (puVar5 == puVar1) break;
    if ((*puVar6 & 0x7fffffff) < param_2) {
      puVar5 = puVar6 + 2;
    }
    else {
      puVar1 = puVar6 + -2;
    }
  }
  if (puVar4 == (uint *)0x0) {
    uVar2 = 0;
  }
  else {
    uVar2 = puVar4[1];
  }
  return uVar2;
}

