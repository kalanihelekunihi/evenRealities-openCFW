
undefined4 os_timer_or_thread_create_wrapper(int param_1,undefined4 param_2,int *param_3)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  undefined4 local_18;
  
  local_18 = 0;
  uVar2 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar2 = getCurrentExceptionNumber();
    uVar2 = uVar2 & 0x1ff;
  }
  if ((uVar2 == 0) && (param_1 != 0)) {
    uVar2 = 0x80;
    iVar4 = 0x18;
    iVar5 = 0;
    iVar3 = -1;
    if (param_3 == (int *)0x0) {
      iVar3 = 0;
    }
    else {
      if (*param_3 != 0) {
        iVar5 = *param_3;
      }
      if (param_3[6] != 0) {
        iVar4 = param_3[6];
      }
      if ((0x37 < iVar4 - 1U) || ((*(byte *)(param_3 + 1) & 1) != 0)) {
        return 0;
      }
      uVar6 = param_3[5];
      if (uVar6 != 0) {
        uVar2 = uVar6 >> 2;
      }
      if ((((param_3[2] == 0) || ((uint)param_3[3] < 0x5c)) || (param_3[4] == 0)) || (uVar6 == 0)) {
        if (((param_3[2] == 0) && (param_3[3] == 0)) && (param_3[4] == 0)) {
          iVar3 = 0;
        }
      }
      else {
        iVar3 = 1;
      }
    }
    if (iVar3 == 1) {
      local_18 = FUN_0800ca06(param_1,iVar5,uVar2,param_2,iVar4,param_3[4],param_3[2]);
    }
    else if ((iVar3 == 0) &&
            (iVar4 = xTaskCreate(param_1,iVar5,uVar2 & 0xffff,param_2,iVar4,&local_18), iVar4 != 1))
    {
      local_18 = 0;
    }
  }
  return local_18;
}

