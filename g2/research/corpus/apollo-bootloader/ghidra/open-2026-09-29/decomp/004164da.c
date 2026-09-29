
undefined8 bl_runtime_create(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 0;
  iVar1 = FUN_0041602a();
  if (iVar1 == 0) {
    iVar1 = -1;
    if (param_1 == 0) {
      iVar1 = 0;
    }
    else if ((*(int *)(param_1 + 8) == 0) || (*(uint *)(param_1 + 0xc) < 0x20)) {
      if ((*(int *)(param_1 + 8) == 0) && (*(int *)(param_1 + 0xc) == 0)) {
        iVar1 = 0;
      }
    }
    else {
      iVar1 = 1;
    }
    if (iVar1 == 1) {
      uVar2 = FUN_00419978(*(undefined4 *)(param_1 + 8));
    }
    else if (iVar1 == 0) {
      uVar2 = FUN_004199bc();
    }
  }
  return CONCAT44(param_4,uVar2);
}

