
undefined8 attsSetupMsg(int param_1,undefined1 param_2,uint param_3,undefined2 *param_4)

{
  char cVar1;
  undefined2 uVar2;
  uint local_20;
  
  cVar1 = *(char *)(param_4 + 4);
  uVar2 = param_4[1];
  attL2cDataReq(*(undefined4 *)(param_1 + 0x10),param_3 & 0xff,*param_4);
  local_20 = param_3;
  if (cVar1 == '\x1d') {
    *(undefined2 *)(param_1 + 0x28) = uVar2;
    *(undefined2 *)(param_1 + 0x26) = *(undefined2 *)(param_1 + 0x28);
    *(undefined1 *)(param_1 + 10) = 0x22;
    uVar2 = attMsgParam(*(undefined1 *)(param_1 + 0x24),*(undefined1 *)(param_1 + 0x25));
    *(undefined2 *)(param_1 + 8) = uVar2;
    WsfTimerStartSec(param_1,*(undefined1 *)(*DAT_00533e94 + 6));
  }
  else if ((int)((uint)*(byte *)(*(int *)(param_1 + 0x10) + (param_3 & 0xff) * 4 + 2) << 0x1e) < 0)
  {
    attsSetPendNtfHandle(param_1,uVar2);
  }
  else if (cVar1 == '#') {
    local_20 = 0;
    attExecCallback(param_2,0x13,uVar2,0);
  }
  else {
    attsExecCallback(param_2,uVar2,0);
  }
  return CONCAT44(param_4,local_20);
}

