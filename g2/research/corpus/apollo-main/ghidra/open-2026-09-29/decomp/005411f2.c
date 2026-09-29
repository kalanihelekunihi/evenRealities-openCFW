
int SVC_FlashDBBlobWrite(uint param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined4 local_28;
  uint local_24;
  
  osKernelGetTickCount();
  local_24 = param_4 & 0xffff;
  local_28 = param_3;
  iVar1 = FUN_0054503a(DAT_005412c8 + (param_1 & 0xff) * 0x8ac,param_2,&local_28);
  osKernelGetTickCount();
  return -iVar1;
}

