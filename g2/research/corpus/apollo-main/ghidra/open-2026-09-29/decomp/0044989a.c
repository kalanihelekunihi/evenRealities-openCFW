
undefined8 osSemaphoreNew(uint param_1,uint param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 local_18;
  
  iVar2 = 0;
  iVar1 = IRQ_Context();
  local_18 = param_4;
  if (((iVar1 == 0) && (param_1 != 0)) && (param_2 <= param_1)) {
    iVar1 = -1;
    if (param_3 == 0) {
      iVar1 = 0;
    }
    else if ((*(int *)(param_3 + 8) == 0) || (*(uint *)(param_3 + 0xc) < 0x50)) {
      if ((*(int *)(param_3 + 8) == 0) && (*(int *)(param_3 + 0xc) == 0)) {
        iVar1 = 0;
      }
    }
    else {
      iVar1 = 1;
    }
    if (iVar1 != -1) {
      if (param_1 == 1) {
        if (iVar1 == 1) {
          local_18 = 3;
          iVar2 = FUN_004415ca(1,0,0,*(undefined4 *)(param_3 + 8));
        }
        else {
          iVar2 = FUN_00441636(1,0,3);
        }
        if (((iVar2 != 0) && (param_2 != 0)) && (iVar1 = FUN_004417ee(iVar2,0,0,0), iVar1 != 1)) {
          vQueueDelete(iVar2);
          iVar2 = 0;
        }
      }
      else if (iVar1 == 1) {
        iVar2 = FUN_00441790(param_1,param_2,*(undefined4 *)(param_3 + 8));
      }
      else {
        iVar2 = FUN_004417c2(param_1,param_2);
      }
    }
  }
  return CONCAT44(local_18,iVar2);
}

