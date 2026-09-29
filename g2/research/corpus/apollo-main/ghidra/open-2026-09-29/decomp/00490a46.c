
undefined8 FUN_00490a46(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  
  if (*(int *)(param_2 + 0x1c) == 0) {
    uVar1 = 1;
  }
  else {
    iVar2 = FUN_00490d66(param_1,param_2);
    if (iVar2 == 0) {
      uVar1 = 0;
    }
    else {
      uVar3 = *(byte *)(param_2 + 0x16) & 0xf;
      if ((*(byte *)(param_2 + 0x16) & 0xf) == 0) {
        uVar1 = FUN_00490e90(param_1,param_2);
      }
      else if (uVar3 - 1 < 3) {
        uVar1 = FUN_00490eae(param_1,param_2);
      }
      else if (uVar3 - 4 < 2) {
        uVar1 = FUN_00490f72(param_1,param_2);
      }
      else if (uVar3 == 6) {
        uVar1 = FUN_00490fa2(param_1,param_2);
      }
      else if (uVar3 == 7) {
        uVar1 = FUN_00490fe4(param_1,param_2);
      }
      else if (uVar3 - 8 < 2) {
        uVar1 = FUN_0049104c(param_1,param_2);
      }
      else if (uVar3 - 8 == 3) {
        uVar1 = FUN_004910e8(param_1,param_2);
      }
      else {
        uVar1 = DAT_004910c0;
        if (*(int *)(param_1 + 0x10) != 0) {
          uVar1 = *(undefined4 *)(param_1 + 0x10);
        }
        *(undefined4 *)(param_1 + 0x10) = uVar1;
        uVar1 = 0;
      }
    }
  }
  return CONCAT44(param_4,uVar1);
}

