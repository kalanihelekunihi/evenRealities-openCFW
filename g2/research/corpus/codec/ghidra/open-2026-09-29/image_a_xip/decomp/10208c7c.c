
undefined4 gx8002_app_resume(void)

{
  int iVar1;
  
  iVar1 = *DAT_10208c94;
  if ((iVar1 != 0) && (*(uint *)(iVar1 + 0x18) != 0)) {
    (*(code *)(*(uint *)(iVar1 + 0x18) & 0xfffffffe))(*(undefined4 *)(iVar1 + 0x1c));
  }
  return 0;
}

