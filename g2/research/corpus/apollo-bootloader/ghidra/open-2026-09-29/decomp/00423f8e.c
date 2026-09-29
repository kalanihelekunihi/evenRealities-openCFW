
void FUN_00423f8e(int param_1)

{
  int iVar1;
  
  iVar1 = clock_request(4,*(int *)(param_1 + 4) + 0x10U & 0xff);
  if (iVar1 == 0) {
    cmdq_enable_427878(*(undefined4 *)(param_1 + 0x828));
  }
  return;
}

