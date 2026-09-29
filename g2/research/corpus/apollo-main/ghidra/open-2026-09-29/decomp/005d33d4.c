
undefined8 FUN_005d33d4(int param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  int iVar4;
  int local_20;
  int local_1c;
  
  iVar4 = 0;
  iVar2 = *(int *)(param_1 + 4);
  puVar3 = *(undefined4 **)(*(int *)(iVar2 + 0x80) + 0x34);
  if (puVar3 == (undefined4 *)0x0) {
    local_20 = *(int *)(*(int *)(iVar2 + 0x1ac) + param_2 * 4);
    local_1c = *(int *)(*(int *)(iVar2 + 0x1b0) + param_2 * 4);
  }
  else {
    local_20 = param_3;
    local_1c = param_4;
    iVar4 = (**(code **)*puVar3)(puVar3[1],param_2,&local_20);
  }
  iVar1 = local_1c;
  iVar2 = local_20;
  if (iVar4 == 0) {
    FUN_0043c0e4(param_3,0x10,0);
    *(int *)(param_3 + 0xc) = iVar2;
    *(undefined4 *)(param_3 + 4) = *(undefined4 *)(param_3 + 0xc);
    *(int *)(param_3 + 8) = iVar2 + iVar1;
  }
  return CONCAT44(local_20,iVar4);
}

