
void smpActStorePin(int param_1,int param_2)

{
  FUN_00439be4(*(undefined4 *)(param_1 + 0x30),param_2 + 4,*(undefined1 *)(param_2 + 0x14));
  if (*(char *)(param_2 + 0x14) == '\x03') {
    FUN_0043c0e4(*(int *)(param_1 + 0x30) + 3,0xd,0);
  }
  return;
}

