
void attcFreePkt(int param_1)

{
  if (*(int *)(param_1 + 4) != 0) {
    WsfMsgFree(*(undefined4 *)(param_1 + 4));
    *(undefined4 *)(param_1 + 4) = 0;
  }
  return;
}

