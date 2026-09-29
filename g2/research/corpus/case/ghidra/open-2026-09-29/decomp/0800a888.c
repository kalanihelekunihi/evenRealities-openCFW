
uint osEventFlagsSet(int param_1,uint param_2,undefined4 param_3,int param_4)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  int local_10;
  
  if ((param_1 == 0) || (param_2 >> 0x18 != 0)) {
    param_2 = 0xfffffffc;
  }
  else {
    uVar3 = 0;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      uVar3 = getCurrentExceptionNumber();
      uVar3 = uVar3 & 0x1ff;
    }
    if (uVar3 == 0) {
      local_10 = param_4;
      uVar3 = case_event_group_set_bits(param_1,param_2);
      return uVar3;
    }
    local_10 = 0;
    iVar2 = case_dispatch_resource4(param_1,param_2,&local_10);
    if (iVar2 == 0) {
      return 0xfffffffd;
    }
    if (local_10 != 0) {
      *(undefined4 *)(DAT_0800a8d4 + 4) = 0x10000000;
      return param_2;
    }
  }
  return param_2;
}

