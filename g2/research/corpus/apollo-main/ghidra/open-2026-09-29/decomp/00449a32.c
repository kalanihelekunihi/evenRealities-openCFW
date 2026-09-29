
undefined8 osMessageQueueNew(int param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_18;
  
  uVar2 = 0;
  iVar1 = IRQ_Context();
  local_18 = param_4;
  if (((iVar1 == 0) && (param_1 != 0)) && (param_2 != 0)) {
    iVar1 = -1;
    if (param_3 == 0) {
      iVar1 = 0;
    }
    else if (((*(int *)(param_3 + 8) == 0) || (*(uint *)(param_3 + 0xc) < 0x50)) ||
            ((*(int *)(param_3 + 0x10) == 0 ||
             (*(uint *)(param_3 + 0x14) < (uint)(param_2 * param_1))))) {
      if (((*(int *)(param_3 + 8) == 0) && (*(int *)(param_3 + 0xc) == 0)) &&
         ((*(int *)(param_3 + 0x10) == 0 && (*(int *)(param_3 + 0x14) == 0)))) {
        iVar1 = 0;
      }
    }
    else {
      iVar1 = 1;
    }
    if (iVar1 == 1) {
      local_18 = 0;
      uVar2 = FUN_004415ca(param_1,param_2,*(undefined4 *)(param_3 + 0x10),
                           *(undefined4 *)(param_3 + 8));
    }
    else if (iVar1 == 0) {
      uVar2 = FUN_00441636(param_1,param_2,0);
    }
  }
  return CONCAT44(local_18,uVar2);
}

