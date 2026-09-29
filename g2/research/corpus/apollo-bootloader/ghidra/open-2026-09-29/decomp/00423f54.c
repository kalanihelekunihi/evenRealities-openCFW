
undefined4 cq_term(int param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_00424aec;
  iVar2 = *(int *)(param_1 + 4);
  if (*(int *)(iVar2 * 0x8d0 + DAT_00424aec + 0x828) != 0) {
    cmdq_term_427ad6(*(undefined4 *)(iVar2 * 0x8d0 + DAT_00424aec + 0x828),1);
    *(undefined4 *)(iVar1 + iVar2 * 0x8d0 + 0x828) = 0;
  }
  return 0;
}

