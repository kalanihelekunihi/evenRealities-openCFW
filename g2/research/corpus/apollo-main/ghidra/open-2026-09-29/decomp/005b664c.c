
void conversate_tag_page_deinit(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_005b6958;
  if ((*(int *)(DAT_005b6958 + 0x88) != 0) &&
     (iVar2 = FUN_0043e2ea(*(undefined4 *)(DAT_005b6958 + 0x88)), iVar2 != 0)) {
    FUN_00441488(*(undefined4 *)(iVar1 + 0x88),0xff,0);
  }
  *(undefined4 *)(iVar1 + 0x88) = 0;
  FUN_0044d90e(*(undefined4 *)(iVar1 + 0x1c));
  *(undefined4 *)(iVar1 + 0x1c) = 0;
  *(undefined1 *)(iVar1 + 0x98) = 0;
  return;
}

