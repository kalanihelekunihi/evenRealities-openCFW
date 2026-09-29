
undefined4 SVC_FlashDBInit(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 in_r3;
  
  _flashDBMutexInit();
  uVar2 = DAT_005412dc;
  uVar1 = DAT_005412d8;
  SVC_KvdbInit(DAT_005412d8,DAT_005412dc);
  SVC_NvdbInit(uVar1,uVar2);
  return in_r3;
}

