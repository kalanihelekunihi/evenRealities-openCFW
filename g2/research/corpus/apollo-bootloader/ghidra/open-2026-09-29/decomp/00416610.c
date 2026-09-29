
uint bl_runtime_flags_create(int param_1)

{
  int iVar1;
  uint uVar2;
  bool bVar3;
  
  uVar2 = 0;
  iVar1 = FUN_0041602a();
  if (iVar1 == 0) {
    if (param_1 == 0) {
      iVar1 = 0;
    }
    else {
      iVar1 = *(int *)(param_1 + 4);
    }
    bVar3 = -1 < iVar1 << 0x1f;
    if (-1 < iVar1 << 0x1c) {
      iVar1 = -1;
      if (param_1 == 0) {
        iVar1 = 0;
      }
      else if ((*(int *)(param_1 + 8) == 0) || (*(uint *)(param_1 + 0xc) < 0x50)) {
        if ((*(int *)(param_1 + 8) == 0) && (*(int *)(param_1 + 0xc) == 0)) {
          iVar1 = 0;
        }
      }
      else {
        iVar1 = 1;
      }
      if (iVar1 == 1) {
        if (bVar3) {
          uVar2 = FUN_00419dc2(1,*(undefined4 *)(param_1 + 8));
        }
        else {
          uVar2 = FUN_00419dc2(4,*(undefined4 *)(param_1 + 8));
        }
      }
      else if (iVar1 == 0) {
        if (bVar3) {
          uVar2 = FUN_00419da8(1);
        }
        else {
          uVar2 = FUN_00419da8(4);
        }
      }
      if ((uVar2 != 0) && (!bVar3)) {
        uVar2 = uVar2 | 1;
      }
    }
  }
  return uVar2;
}

