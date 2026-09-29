
undefined4 FUN_00590cf4(int param_1,char param_2)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_00590d34;
  iVar2 = *(int *)(param_1 + 4);
  *(undefined4 *)(DAT_00590d34 + iVar2 * 0x1000 + 0x200) = 0;
  if (param_2 == '\0') {
    *(undefined4 *)(iVar1 + iVar2 * 0x1000 + 0x20c) = 0;
  }
  else if (param_2 == '\x01') {
    *(undefined4 *)(iVar1 + iVar2 * 0x1000 + 0x218) = 0;
  }
  return 0;
}

