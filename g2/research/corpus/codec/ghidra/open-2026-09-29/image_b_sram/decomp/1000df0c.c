
void FUN_1000df0c(int param_1,int param_2,int param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  if (0 < param_3) {
    iVar1 = 0;
    do {
      uVar2 = *(undefined4 *)(param_2 + iVar1 * 4);
      FUN_10011af4();
      FUN_1000fbb0();
      FUN_10012398();
      *(undefined4 *)(param_1 + iVar1 * 4) = uVar2;
      iVar1 = iVar1 + 1;
    } while (param_3 != iVar1);
  }
  return;
}

