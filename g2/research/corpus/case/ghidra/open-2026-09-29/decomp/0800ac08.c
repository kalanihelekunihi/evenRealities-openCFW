
void FUN_0800ac08(int param_1)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  
  FUN_0800bffc();
  piVar1 = DAT_0800ac7c;
  DAT_0800ac7c[2] = DAT_0800ac7c[2] + 1;
  if (*piVar1 == 0) {
    *piVar1 = param_1;
    if (piVar1[2] == 1) {
      FUN_0800af70();
    }
  }
  else if ((piVar1[5] == 0) && (*(uint *)(*piVar1 + 0x2c) <= *(uint *)(param_1 + 0x2c))) {
    *piVar1 = param_1;
  }
  iVar2 = piVar1[9];
  piVar1[9] = iVar2 + 1;
  *(int *)(param_1 + 0x44) = iVar2 + 1;
  uVar3 = *(uint *)(param_1 + 0x2c);
  if ((uint)piVar1[4] < uVar3) {
    piVar1[4] = uVar3;
  }
  FUN_0800bfe2(uVar3 * 0x14 + DAT_0800ac80,param_1 + 4);
  FUN_0800c014();
  if ((piVar1[5] != 0) && (*(uint *)(*piVar1 + 0x2c) < *(uint *)(param_1 + 0x2c))) {
    FUN_0800c0a0();
  }
  return;
}

