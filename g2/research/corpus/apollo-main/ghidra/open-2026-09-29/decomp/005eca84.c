
undefined1 FUN_005eca84(void)

{
  undefined1 uVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = td_state_ptr_alias1();
  iVar3 = UX_GetSystemBLEStatus();
  if (((iVar3 == 0) || (iVar2 == 0)) || (*(char *)(iVar2 + 0xa1d8) != '\x02')) {
    uVar1 = 0;
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

