
int FUN_005d23ba(int param_1,uint param_2)

{
  if (*(uint *)(param_1 + 0x14) <= param_2) {
    FUN_005d2a0a(*(undefined4 *)(param_1 + 4),0x82);
    param_2 = 0;
  }
  return *(int *)(param_1 + 0x1c) + *(int *)(param_1 + 8) * param_2;
}

