
undefined8 hash_lookup(undefined4 param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  piVar3 = *(int **)(param_2 + 0x14);
  uStack_14 = param_1;
  uVar1 = (**(code **)(param_2 + 0xc))(&uStack_14);
  piVar4 = piVar3 + (uVar1 - *(uint *)(param_2 + 4) * (uVar1 / *(uint *)(param_2 + 4)));
  while ((*piVar4 != 0 && (iVar2 = (**(code **)(param_2 + 0x10))(*piVar4,&uStack_14), iVar2 == 0)))
  {
    piVar4 = piVar4 + -1;
    if (piVar4 < piVar3) {
      piVar4 = piVar3 + *(int *)(param_2 + 4) + -1;
    }
  }
  return CONCAT44(uStack_18,piVar4);
}

