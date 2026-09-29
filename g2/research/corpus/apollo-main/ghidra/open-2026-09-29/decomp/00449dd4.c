
undefined8 osMemoryPoolFree(int param_1,uint param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int local_18;
  
  local_18 = param_4;
  if ((param_1 == 0) || (param_2 == 0)) {
    uVar3 = 0xfffffffc;
  }
  else if ((*(uint *)(param_1 + 0x20) & DAT_00449e90) == DAT_00449e90) {
    if ((param_2 < *(uint *)(param_1 + 8)) ||
       ((*(int *)(param_1 + 8) + *(int *)(param_1 + 0xc)) - 1U < param_2)) {
      uVar3 = 0xfffffffc;
    }
    else {
      uVar3 = 0;
      iVar1 = IRQ_Context();
      if (iVar1 == 0) {
        iVar1 = FUN_00441e66(*(undefined4 *)(param_1 + 4));
        if (iVar1 == *(int *)(param_1 + 0x18)) {
          uVar3 = 0xfffffffd;
        }
        else {
          FUN_004420d0();
          FreeBlock(param_1,param_2);
          FUN_004420e8();
          FUN_004417ee(*(undefined4 *)(param_1 + 4),0,0,0);
        }
      }
      else {
        iVar1 = FUN_00441e8a(*(undefined4 *)(param_1 + 4));
        if (iVar1 == *(int *)(param_1 + 0x18)) {
          uVar3 = 0xfffffffd;
        }
        else {
          uVar2 = ulSetInterruptMask();
          FreeBlock(param_1,param_2);
          vClearInterruptMask(uVar2);
          local_18 = 0;
          FUN_00441a42(*(undefined4 *)(param_1 + 4),&local_18);
          if (local_18 != 0) {
            *DAT_00449e94 = 0x10000000;
          }
        }
      }
    }
  }
  else {
    uVar3 = 0xfffffffd;
  }
  return CONCAT44(local_18,uVar3);
}

