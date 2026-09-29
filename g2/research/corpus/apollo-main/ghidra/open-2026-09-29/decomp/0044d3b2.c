
void FUN_0044d3b2(int param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int *piVar4;
  
  iVar1 = FUN_0043e1be(param_1);
  if (iVar1 == 0) {
    return;
  }
  if ((*(int *)(iVar1 + 0xc) != 0) && (**(int **)(iVar1 + 0xc) == param_1)) {
    if ((int)((uint)*(byte *)(iVar1 + 0x1c) << 0x1f) < 0) {
      *(byte *)(iVar1 + 0x1c) = *(byte *)(iVar1 + 0x1c) & 0xfe;
    }
    iVar2 = FUN_00482cd8(iVar1);
    if ((iVar2 == *(int *)(iVar1 + 0xc)) &&
       (iVar2 = FUN_00482ce4(iVar1), iVar2 == *(int *)(iVar1 + 0xc))) {
      uVar3 = FUN_0044d77a(iVar1);
      FUN_00451670(**(undefined4 **)(iVar1 + 0xc),0x14,uVar3);
    }
    else {
      FUN_0044d5f8(iVar1);
    }
  }
  if ((*(int *)(iVar1 + 0xc) != 0) && (**(int **)(iVar1 + 0xc) == param_1)) {
    *(undefined4 *)(iVar1 + 0xc) = 0;
  }
  piVar4 = (int *)FUN_00482cd8(iVar1);
  while( true ) {
    if (piVar4 == (int *)0x0) {
      return;
    }
    if (*piVar4 == param_1) break;
    piVar4 = (int *)FUN_00482cf0(iVar1,piVar4);
  }
  FUN_00482c0e(iVar1,piVar4);
  FUN_0044f758(piVar4);
  if (*(int *)(param_1 + 8) == 0) {
    return;
  }
  *(undefined4 *)(*(int *)(param_1 + 8) + 4) = 0;
  return;
}

