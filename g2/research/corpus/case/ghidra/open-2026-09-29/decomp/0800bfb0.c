
void FUN_0800bfb0(int *param_1,uint *param_2)

{
  uint *puVar1;
  uint *puVar2;
  uint uVar3;
  
  if (*param_2 == 0xffffffff) {
    puVar2 = (uint *)param_1[4];
  }
  else {
    puVar1 = (uint *)(param_1 + 2);
    do {
      puVar2 = puVar1;
      puVar1 = (uint *)puVar2[1];
    } while (*(uint *)puVar2[1] <= *param_2);
  }
  uVar3 = puVar2[1];
  param_2[1] = uVar3;
  *(uint **)(uVar3 + 8) = param_2;
  param_2[2] = (uint)puVar2;
  puVar2[1] = (uint)param_2;
  param_2[4] = (uint)param_1;
  *param_1 = *param_1 + 1;
  return;
}

