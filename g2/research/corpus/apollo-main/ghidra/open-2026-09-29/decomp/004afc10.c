
void nvdbSysDtResetAging(void)

{
  int iVar1;
  undefined1 auStack_30 [40];
  
  FUN_0048949c(auStack_30,0x28);
  iVar1 = DAT_004b036c;
  FUN_00439c04(DAT_004b036c + 0x30,auStack_30,0x28);
  FUN_00439c04(iVar1 + 0x58,auStack_30,0x28);
  FUN_00439c04(iVar1 + 0x80,auStack_30,0x28);
  *(undefined1 *)(iVar1 + 0xa8) = 0;
  *(undefined1 *)(iVar1 + 0xa9) = 0;
  *(undefined1 *)(iVar1 + 0xab) = 0;
  SVC_NvdbWriteSysData(10,iVar1 + 0xa9);
  return;
}

