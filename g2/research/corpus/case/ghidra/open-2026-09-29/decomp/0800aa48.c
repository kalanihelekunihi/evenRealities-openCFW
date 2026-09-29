
int os_timer_or_thread_create_wrapper(int param_1,int param_2,int param_3,int *param_4)

{
  bool bVar1;
  uint uVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  iVar5 = 0;
  uVar2 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar2 = getCurrentExceptionNumber();
    uVar2 = uVar2 & 0x1ff;
  }
  if (((uVar2 == 0) && (param_1 != 0)) && (piVar3 = (int *)pvPortMalloc(8), piVar3 != (int *)0x0)) {
    *piVar3 = param_1;
    piVar3[1] = param_3;
    iVar4 = -1;
    iVar6 = 0;
    if (param_4 == (int *)0x0) {
      iVar4 = 0;
    }
    else {
      if (*param_4 != 0) {
        iVar6 = *param_4;
      }
      if ((param_4[2] == 0) || ((uint)param_4[3] < 0x2c)) {
        if ((param_4[2] == 0) && (param_4[3] == 0)) {
          iVar4 = 0;
        }
      }
      else {
        iVar4 = 1;
      }
    }
    if (iVar4 == 1) {
      iVar5 = FUN_0800ccf2(iVar6,1,param_2 != 0,piVar3,DAT_0800aaec,param_4[2]);
    }
    else if (iVar4 == 0) {
      iVar5 = FUN_0800ccc0(iVar6,1,param_2 != 0,piVar3,DAT_0800aaec);
    }
    if (iVar5 == 0) {
      FUN_0800c030(piVar3);
    }
  }
  return iVar5;
}

