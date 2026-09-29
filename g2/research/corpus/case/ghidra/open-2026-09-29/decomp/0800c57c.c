
undefined4 FUN_0800c57c(void)

{
  int iVar1;
  
  iVar1 = DAT_0800c5a4;
  *(uint *)(DAT_0800c5a4 + 0x20) = *(uint *)(DAT_0800c5a4 + 0x20) | 0xff0000;
  *(uint *)(iVar1 + 0x20) = *(uint *)(iVar1 + 0x20) | 0xff000000;
  FUN_0800c078();
  *DAT_0800c5a8 = 0;
  vPortStartFirstTask();
  return 0;
}

