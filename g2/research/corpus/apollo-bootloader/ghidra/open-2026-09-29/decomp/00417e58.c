
void FUN_00417e58(int param_1)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  
  FUN_0041b3e4();
  piVar1 = DAT_0041855c;
  *DAT_0041855c = *DAT_0041855c + 1;
  piVar2 = DAT_00418560;
  if (*DAT_00418560 == 0) {
    *DAT_00418560 = param_1;
    if (*piVar1 == 1) {
      FUN_00418a44();
    }
  }
  else if ((*DAT_004186d0 == 0) && (*(uint *)(*DAT_00418560 + 0x2c) <= *(uint *)(param_1 + 0x2c))) {
    *DAT_00418560 = param_1;
  }
  piVar1 = DAT_00418564;
  *DAT_00418564 = *DAT_00418564 + 1;
  *(int *)(param_1 + 0x58) = *piVar1;
  if (*DAT_00418568 < *(uint *)(param_1 + 0x2c)) {
    *DAT_00418568 = *(uint *)(param_1 + 0x2c);
  }
  iVar3 = DAT_0041856c;
  iVar4 = *(int *)(*(int *)(param_1 + 0x2c) * 0x14 + DAT_0041856c + 4);
  *(int *)(param_1 + 8) = iVar4;
  *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)(iVar4 + 8);
  *(int *)(*(int *)(iVar4 + 8) + 4) = param_1 + 4;
  *(int *)(iVar4 + 8) = param_1 + 4;
  *(int *)(param_1 + 0x14) = *(int *)(param_1 + 0x2c) * 0x14 + iVar3;
  *(int *)(iVar3 + *(int *)(param_1 + 0x2c) * 0x14) =
       *(int *)(iVar3 + *(int *)(param_1 + 0x2c) * 0x14) + 1;
  FUN_0041b3fc();
  if (*DAT_004186d0 != 0) {
    if (*(uint *)(*piVar2 + 0x2c) < *(uint *)(param_1 + 0x2c)) {
      FUN_0041b3d0();
    }
  }
  return;
}

