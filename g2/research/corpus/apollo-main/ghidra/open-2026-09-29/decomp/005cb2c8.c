
void FUN_005cb2c8(int param_1,int param_2,ushort param_3)

{
  if (*(int *)(param_1 + 0x58) < (int)(uint)param_3) {
    *(undefined4 *)(param_2 + 0x1c) = 0;
  }
  else if (*(int *)(*(int *)(param_1 + 0x38) + (uint)param_3 * 4 + -4) == 0) {
    *(undefined4 *)(param_2 + 0x1c) = 0;
  }
  else {
    *(undefined4 *)(param_2 + 0x1c) =
         *(undefined4 *)(*(int *)(param_1 + 0x38) + (uint)param_3 * 4 + -4);
    *(byte *)(param_2 + 0x54) = *(byte *)(param_2 + 0x54) & 0xfe;
  }
  return;
}

