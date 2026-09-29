
void lfs_mlist_append(int param_1,undefined4 *param_2)

{
  *param_2 = *(undefined4 *)(param_1 + 0x28);
  *(undefined4 **)(param_1 + 0x28) = param_2;
  return;
}

