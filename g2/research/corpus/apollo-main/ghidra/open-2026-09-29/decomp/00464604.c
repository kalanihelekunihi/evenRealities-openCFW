
undefined8 FUN_00464604(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  byte bVar4;
  
  if ((int)((uint)*(byte *)(param_1 + 0x14) << 0x1f) < 0) {
    uVar1 = 0;
  }
  else {
    bVar4 = 0;
    iVar2 = FUN_0046467c(param_1);
    if (iVar2 == 0) {
      iVar2 = *(int *)(param_1 + 0x10);
      if (0 < *(int *)(param_1 + 0x10)) {
        *(int *)(param_1 + 0x10) = *(int *)(param_1 + 0x10) + -1;
      }
      uVar3 = FUN_00473482();
      *(undefined4 *)(param_1 + 4) = uVar3;
      if ((*(int *)(param_1 + 8) != 0) && (iVar2 != 0)) {
        (**(code **)(param_1 + 8))(param_1);
      }
      bVar4 = 1;
    }
    if ((*(char *)(DAT_004646b8 + 0x82) == '\0') && (*(int *)(param_1 + 0x10) == 0)) {
      if (*(int *)(param_1 + 0x14) << 0x1e < 0) {
        FUN_004644ee(param_1);
      }
      else {
        FUN_0046450c(param_1);
      }
    }
    uVar1 = (uint)bVar4;
  }
  return CONCAT44(param_4,uVar1);
}

