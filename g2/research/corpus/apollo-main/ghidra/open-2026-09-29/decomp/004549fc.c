
void FUN_004549fc(int param_1)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  
  FUN_004420d0();
  piVar1 = DAT_004551a0;
  *DAT_004551a0 = *DAT_004551a0 + 1;
  piVar2 = DAT_004551a4;
  if (*DAT_004551a4 == 0) {
    *DAT_004551a4 = param_1;
    if (*piVar1 == 1) {
      FUN_0045568c();
    }
  }
  else if ((*DAT_00455314 == 0) && (*(uint *)(*DAT_004551a4 + 0x2c) <= *(uint *)(param_1 + 0x2c))) {
    *DAT_004551a4 = param_1;
  }
  piVar1 = DAT_004551a8;
  *DAT_004551a8 = *DAT_004551a8 + 1;
  *(int *)(param_1 + 0x58) = *piVar1;
  if (*DAT_004551ac < *(uint *)(param_1 + 0x2c)) {
    *DAT_004551ac = *(uint *)(param_1 + 0x2c);
  }
  iVar3 = DAT_004551b0;
  iVar4 = *(int *)(*(int *)(param_1 + 0x2c) * 0x14 + DAT_004551b0 + 4);
  *(int *)(param_1 + 8) = iVar4;
  *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)(iVar4 + 8);
  *(int *)(*(int *)(iVar4 + 8) + 4) = param_1 + 4;
  *(int *)(iVar4 + 8) = param_1 + 4;
  *(int *)(param_1 + 0x14) = *(int *)(param_1 + 0x2c) * 0x14 + iVar3;
  *(int *)(iVar3 + *(int *)(param_1 + 0x2c) * 0x14) =
       *(int *)(iVar3 + *(int *)(param_1 + 0x2c) * 0x14) + 1;
  FUN_004420e8();
  if (*DAT_00455314 != 0) {
    if (*(uint *)(*piVar2 + 0x2c) < *(uint *)(param_1 + 0x2c)) {
      FUN_004420bc();
    }
  }
  return;
}

