
void td_session_ring_reset(void)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  
  piVar2 = DAT_00597c04;
  iVar1 = DAT_00597be0;
  *DAT_00597c04 = *DAT_00597c04 + 1;
  iVar3 = *piVar2;
  FUN_0043c0e4(iVar1,0x850c,0);
  *(int *)(iVar1 + 0x8504) = iVar3;
  *(undefined4 *)(iVar1 + 0x8508) = 1;
  return;
}

