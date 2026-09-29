
undefined4 osThreadNew(int param_1,undefined4 param_2,int *param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  undefined4 local_1c;
  undefined4 uStack_18;
  
  local_1c = 0;
  uStack_18 = param_4;
  iVar1 = IRQ_Context();
  if ((iVar1 == 0) && (param_1 != 0)) {
    uVar3 = 0x400;
    uVar2 = 0x18;
    iVar1 = 0;
    iVar4 = -1;
    if (param_3 == (int *)0x0) {
      iVar4 = 0;
    }
    else {
      if (*param_3 != 0) {
        iVar1 = *param_3;
      }
      if (param_3[6] != 0) {
        uVar2 = param_3[6];
      }
      if (((uVar2 == 0) || (0x38 < uVar2)) || ((int)((uint)*(byte *)(param_3 + 1) << 0x1f) < 0)) {
        return 0;
      }
      if (param_3[5] != 0) {
        uVar3 = (uint)param_3[5] >> 2;
      }
      if (((param_3[2] == 0) || ((uint)param_3[3] < 0x70)) ||
         ((param_3[4] == 0 || (param_3[5] == 0)))) {
        if (((param_3[2] == 0) && (param_3[3] == 0)) && (param_3[4] == 0)) {
          iVar4 = 0;
        }
      }
      else {
        iVar4 = 1;
      }
    }
    if (iVar4 == 1) {
      local_1c = FUN_00454820(param_1,iVar1,uVar3,param_2,uVar2,param_3[4],param_3[2]);
    }
    else if ((iVar4 == 0) &&
            (iVar1 = FUN_004548ba(param_1,iVar1,uVar3 & 0xffff,param_2,uVar2,&local_1c), iVar1 != 1)
            ) {
      local_1c = 0;
    }
  }
  return local_1c;
}

