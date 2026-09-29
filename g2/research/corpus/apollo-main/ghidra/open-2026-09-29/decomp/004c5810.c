
uint DmSetPhy(undefined1 param_1,undefined1 param_2,undefined1 param_3,uint param_4,ushort param_5)

{
  int iVar1;
  undefined4 local_18;
  
  WsfTaskLock();
  iVar1 = dmConnCcbById(param_1);
  WsfTaskUnlock();
  local_18 = param_4;
  if (iVar1 != 0) {
    local_18 = (uint)param_5;
    HciLeSetPhyCmd(*(undefined2 *)(iVar1 + 0xc),param_2,param_3,param_4 & 0xff);
  }
  return local_18;
}

