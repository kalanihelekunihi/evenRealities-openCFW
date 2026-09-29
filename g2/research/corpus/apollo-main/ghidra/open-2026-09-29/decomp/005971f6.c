
void td_temp_record_invalidate(void)

{
  int iVar1;
  undefined4 *puVar2;
  
  iVar1 = DAT_00597c08;
  puVar2 = (undefined4 *)(DAT_00597c08 + 0x956c);
  FUN_0043c0e4(puVar2,0x90,0);
  *puVar2 = 0xffffffff;
  *(undefined1 *)(iVar1 + 0x95f2) = 0;
  *(undefined4 *)(iVar1 + 0x9564) = 0xffffffff;
  *(undefined1 *)(iVar1 + 0xa1da) = 1;
  return;
}

