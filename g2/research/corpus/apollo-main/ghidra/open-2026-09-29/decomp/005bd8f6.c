
int FUN_005bd8f6(int param_1,int param_2,int param_3)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  
  iVar4 = *(int *)(param_2 + 0xc);
  uVar5 = *(uint *)(param_1 + 0x30);
  if (*(uint *)(param_1 + 0x34) < uVar5) {
    iVar2 = *(int *)(param_1 + 0x2c);
  }
  else {
    iVar2 = *(int *)(param_1 + 0x34);
  }
  uVar3 = iVar2 - uVar5;
  if (*(uint *)(param_2 + 0x10) < uVar3) {
    uVar3 = *(uint *)(param_2 + 0x10);
  }
  if ((uVar3 != 0) && (param_3 == -5)) {
    param_3 = 0;
  }
  *(uint *)(param_2 + 0x10) = *(int *)(param_2 + 0x10) - uVar3;
  *(uint *)(param_2 + 0x14) = uVar3 + *(int *)(param_2 + 0x14);
  if (*(int *)(param_1 + 0x38) != 0) {
    uVar1 = (**(code **)(param_1 + 0x38))(*(undefined4 *)(param_1 + 0x3c),uVar5,uVar3);
    *(undefined4 *)(param_1 + 0x3c) = uVar1;
    *(undefined4 *)(param_2 + 0x30) = uVar1;
  }
  FUN_00439be4(iVar4,uVar5,uVar3);
  iVar4 = iVar4 + uVar3;
  iVar2 = uVar5 + uVar3;
  if (iVar2 == *(int *)(param_1 + 0x2c)) {
    iVar2 = *(int *)(param_1 + 0x28);
    if (*(int *)(param_1 + 0x34) == *(int *)(param_1 + 0x2c)) {
      *(undefined4 *)(param_1 + 0x34) = *(undefined4 *)(param_1 + 0x28);
    }
    uVar5 = *(int *)(param_1 + 0x34) - iVar2;
    if (*(uint *)(param_2 + 0x10) < uVar5) {
      uVar5 = *(uint *)(param_2 + 0x10);
    }
    if ((uVar5 != 0) && (param_3 == -5)) {
      param_3 = 0;
    }
    *(uint *)(param_2 + 0x10) = *(int *)(param_2 + 0x10) - uVar5;
    *(uint *)(param_2 + 0x14) = uVar5 + *(int *)(param_2 + 0x14);
    if (*(int *)(param_1 + 0x38) != 0) {
      uVar1 = (**(code **)(param_1 + 0x38))(*(undefined4 *)(param_1 + 0x3c),iVar2,uVar5);
      *(undefined4 *)(param_1 + 0x3c) = uVar1;
      *(undefined4 *)(param_2 + 0x30) = uVar1;
    }
    FUN_00439be4(iVar4,iVar2,uVar5);
    iVar4 = iVar4 + uVar5;
    iVar2 = iVar2 + uVar5;
  }
  *(int *)(param_2 + 0xc) = iVar4;
  *(int *)(param_1 + 0x30) = iVar2;
  return param_3;
}

