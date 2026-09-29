
undefined4 td_temp_record_clear(void)

{
  int iVar1;
  undefined4 in_r3;
  
  iVar1 = DAT_00597c08;
  FUN_0043c0e4(DAT_00597c08 + 0x956c,0x90,0);
  if (*(int *)(iVar1 + 0x9564) == -1) {
    *(undefined4 *)(iVar1 + 0x9564) = 0;
  }
  return in_r3;
}

