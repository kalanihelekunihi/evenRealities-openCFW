
undefined4 FUN_004bfc86(int param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_004c08a4;
  iVar2 = *(int *)(param_1 + 4);
  if (*(int *)(iVar2 * 0x8d0 + DAT_004c08a4 + 0x828) != 0) {
    FUN_0053909a(*(undefined4 *)(iVar2 * 0x8d0 + DAT_004c08a4 + 0x828),1);
    *(undefined4 *)(iVar1 + iVar2 * 0x8d0 + 0x828) = 0;
  }
  return 0;
}

