
void FUN_004396c2(int param_1,byte *param_2)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  
  uVar2 = *(uint *)(param_1 + 0x20);
  bVar1 = *param_2;
  iVar3 = uVar2 + 1;
  if (iVar3 < 0x21) {
    *(int *)(param_1 + 0x20) = iVar3;
    *(uint *)(param_1 + 0x1c) = (uint)bVar1 << (uVar2 & 0xff) | *(uint *)(param_1 + 0x1c);
  }
  else {
    FUN_00439b12(param_1,(uint)bVar1,1);
  }
  uVar2 = *(uint *)(param_1 + 0x20);
  iVar3 = *(int *)(param_2 + 4);
  iVar4 = uVar2 + 9;
  if (iVar4 < 0x21) {
    *(int *)(param_1 + 0x20) = iVar4;
    *(uint *)(param_1 + 0x1c) = iVar3 << (uVar2 & 0xff) | *(uint *)(param_1 + 0x1c);
    return;
  }
  FUN_00439b12(param_1,iVar3,9);
  return;
}

