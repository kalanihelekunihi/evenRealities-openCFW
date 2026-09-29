
undefined8 FUN_005d2250(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  
  iVar5 = *(int *)(*(int *)(param_1 + 4) + 0x2a4);
  iVar3 = iVar5 + 0x55c;
  uVar4 = 0;
  if (*(int *)(iVar5 + 0x7e8) != 0) {
    uVar1 = (**(code **)(*(int *)(iVar5 + 0xc10) + 8))(iVar5 + 0xbec,param_3);
    if (*(uint *)(iVar5 + 0x7e8) <= (uVar1 & 0xff)) {
      uVar4 = 3;
      goto LAB_005d22ec;
    }
    iVar3 = *(int *)(iVar5 + (uVar1 & 0xff) * 4 + 0x7ec);
    if ((*(int *)(param_1 + 0x44) != 0) && (param_2 != 0)) {
      *(undefined4 *)(param_1 + 0x48) =
           *(undefined4 *)(**(int **)(param_2 + 0x28) + (uVar1 & 0xff) * 4 + 4);
    }
  }
  *(undefined4 *)(param_1 + 0x2d8) = *(undefined4 *)(iVar3 + 0x26c);
  *(undefined4 *)(param_1 + 0x2e8) = *(undefined4 *)(iVar3 + 0x284);
  uVar2 = FUN_005d2170(*(undefined4 *)(*(int *)(param_1 + 0x6c) + 0x588),
                       *(undefined4 *)(param_1 + 0x2d8));
  *(undefined4 *)(param_1 + 0x2e0) = uVar2;
  *(undefined4 *)(param_1 + 0x248) = *(undefined4 *)(iVar3 + 0x21c);
  *(undefined4 *)(param_1 + 0x24c) = *(undefined4 *)(iVar3 + 0x220);
  *(int *)(param_1 + 0x2fc) = iVar3;
LAB_005d22ec:
  return CONCAT44(param_4,uVar4);
}

