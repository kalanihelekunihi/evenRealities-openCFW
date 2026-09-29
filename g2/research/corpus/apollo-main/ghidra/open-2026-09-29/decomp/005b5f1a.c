
undefined4 conversate_tag_close_timer_callback(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 in_r3;
  
  iVar1 = DAT_005b6958;
  uVar2 = FUN_0044dce2(*(undefined4 *)(DAT_005b6958 + 0x1c),1);
  FUN_0043dfa4(uVar2,1);
  FUN_0058c238(uVar2,200,0);
  *(undefined1 *)(iVar1 + 0x98) = 0;
  return in_r3;
}

