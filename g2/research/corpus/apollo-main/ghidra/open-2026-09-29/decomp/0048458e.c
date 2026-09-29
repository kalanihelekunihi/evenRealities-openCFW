
undefined8 FUN_0048458e(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 *puVar3;
  int *piVar4;
  byte bVar5;
  int *piVar6;
  
  piVar6 = (int *)*(int *)(param_2 + 0x44);
  piVar1 = (int *)0x0;
  while (piVar4 = piVar1, piVar1 = piVar6, piVar1 != (int *)0x0) {
    piVar6 = (int *)*piVar1;
    if (piVar1[0x14] == 3) {
      FUN_004848e8(piVar1,param_1);
      if (piVar4 == (int *)0x0) {
        *(int **)(param_2 + 0x44) = piVar6;
        piVar1 = piVar4;
      }
      else {
        *piVar4 = (int)piVar6;
        piVar1 = piVar4;
      }
    }
  }
  bVar5 = 0;
  if (((*(int *)(param_2 + 0x48) == 0) || (*(char *)(param_2 + 0x50) == '\0')) ||
     (*(int *)(param_2 + 0x44) != 0)) {
    for (puVar3 = *(undefined4 **)(DAT_004849a8 + 0x13c); puVar3 != (undefined4 *)0x0;
        puVar3 = (undefined4 *)*puVar3) {
      iVar2 = (*(code *)puVar3[3])(puVar3,param_2);
      if (iVar2 != -1) {
        bVar5 = 1;
      }
    }
  }
  else {
    for (puVar3 = *(undefined4 **)(*(int *)(param_2 + 0x48) + 0x44); puVar3 != (undefined4 *)0x0;
        puVar3 = (undefined4 *)*puVar3) {
      if (((*(char *)(puVar3 + 1) == '\a') && (puVar3[0x14] == 0)) &&
         (*(int *)(puVar3[0x15] + 0x1c) == param_2)) {
        puVar3[0x14] = 1;
        FUN_0048462e();
        break;
      }
    }
  }
  return CONCAT44(param_4,(uint)bVar5);
}

