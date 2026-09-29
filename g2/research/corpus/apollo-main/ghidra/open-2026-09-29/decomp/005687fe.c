
void FUN_005687fe(int param_1,undefined4 param_2,undefined1 param_3,undefined1 param_4,
                 undefined4 param_5)

{
  if (param_1 != 0) {
    *(undefined4 *)(param_1 + 0x30) = param_2;
    *(undefined1 *)(param_1 + 0x29) = param_3;
    *(undefined1 *)(param_1 + 0x2a) = param_4;
    *(undefined4 *)(param_1 + 0x2c) = param_5;
    if (*(int *)(param_1 + 0x2c) < 0x10000) {
      *(undefined4 *)(param_1 + 0x2c) = 0x10000;
    }
    *(undefined1 *)(param_1 + 0x2b) = param_4;
    FUN_0056882a();
  }
  return;
}

