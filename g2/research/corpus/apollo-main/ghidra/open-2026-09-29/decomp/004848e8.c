
undefined8 FUN_004848e8(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  int *piVar3;
  undefined4 local_18;
  
  local_18 = param_3;
  if (*(char *)(param_1 + 4) == '\a') {
    piVar3 = *(int **)(*(int *)(param_1 + 0x54) + 0x1c);
    if (*piVar3 != 0) {
      iVar1 = FUN_004515a4(piVar3 + 1);
      uVar2 = (*(uint *)(*piVar3 + 8) & 0xffff) * iVar1;
      if (*(uint *)(DAT_004849a8 + 0x144) < uVar2) {
        *(undefined4 *)(DAT_004849a8 + 0x144) = 0;
        local_18 = DAT_004849f4;
        FUN_0044d25c(2,DAT_004849bc,0x230,DAT_004849f8);
      }
      else {
        *(uint *)(DAT_004849a8 + 0x144) = *(int *)(DAT_004849a8 + 0x144) - uVar2;
      }
      FUN_0048b216(*piVar3);
      *piVar3 = 0;
    }
    if (param_2 != 0) {
      for (iVar1 = *(int *)(param_2 + 0x2ac); iVar1 != 0; iVar1 = *(int *)(iVar1 + 0x4c)) {
        if (*(int **)(iVar1 + 0x4c) == piVar3) {
          *(int *)(iVar1 + 0x4c) = piVar3[0x13];
          break;
        }
      }
      if (*(int *)(param_2 + 0x2b4) != 0) {
        (**(code **)(param_2 + 0x2b4))(param_2,piVar3);
      }
      FUN_0044f758(piVar3);
    }
  }
  iVar1 = FUN_00489fc8(param_1);
  if ((iVar1 != 0) && ((int)((uint)*(byte *)(iVar1 + 0x54) << 0x1f) < 0)) {
    FUN_0044f758(*(undefined4 *)(iVar1 + 0x1c));
    *(undefined4 *)(iVar1 + 0x1c) = 0;
  }
  FUN_0044f758(*(undefined4 *)(param_1 + 0x54));
  FUN_0044f758(param_1);
  return CONCAT44(param_4,local_18);
}

