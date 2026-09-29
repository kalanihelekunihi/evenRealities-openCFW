
void FUN_0800c078(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_0800c098;
  *(undefined4 *)(DAT_0800c098 + 0x10) = 0;
  *(undefined4 *)(iVar1 + 0x18) = 0;
  iVar2 = __aeabi_uidiv(*DAT_0800c09c,1000);
  *(int *)(iVar1 + 0x14) = iVar2 + -1;
  *(undefined4 *)(iVar1 + 0x10) = 7;
  return;
}

