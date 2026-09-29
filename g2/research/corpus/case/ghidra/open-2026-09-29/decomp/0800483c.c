
int case_guarded_two_stage(int param_1)

{
  int iVar1;
  
  if (*(char *)(param_1 + 0x54) == '\x01') {
    return 2;
  }
  *(undefined1 *)(param_1 + 0x54) = 1;
  iVar1 = case_wait_controller_flag2(param_1);
  if ((iVar1 == 0) && (iVar1 = case_start_controller_flag0(param_1), iVar1 == 0)) {
    *(uint *)(param_1 + 0x58) = *(uint *)(param_1 + 0x58) & 0xfffffeff | 1;
  }
  *(undefined1 *)(param_1 + 0x54) = 0;
  return iVar1;
}

