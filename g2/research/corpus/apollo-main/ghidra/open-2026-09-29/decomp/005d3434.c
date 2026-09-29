
undefined8 FUN_005d3434(int param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = *(int *)(param_1 + 4);
  uVar1 = *(undefined4 *)(param_2 + 4);
  iVar4 = *(int *)(param_2 + 8);
  iVar2 = *(int *)(param_2 + 4);
  if (*(int *)(*(int *)(iVar3 + 0x80) + 0x34) != 0) {
    (**(code **)(**(int **)(*(int *)(iVar3 + 0x80) + 0x34) + 4))
              (*(undefined4 *)(*(int *)(*(int *)(iVar3 + 0x80) + 0x34) + 4),&stack0xfffffff0);
  }
  return CONCAT44(iVar4 - iVar2,uVar1);
}

