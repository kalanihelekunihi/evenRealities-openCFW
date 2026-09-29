
void FUN_00455728(int param_1,int *param_2,int param_3,char param_4)

{
  undefined1 uVar1;
  undefined2 uVar2;
  
  if (param_1 == 0) {
    param_1 = *DAT_0045605c;
  }
  *param_2 = param_1;
  param_2[1] = param_1 + 0x34;
  param_2[4] = *(int *)(param_1 + 0x2c);
  param_2[7] = *(int *)(param_1 + 0x30);
  param_2[2] = *(int *)(param_1 + 0x58);
  param_2[5] = *(int *)(param_1 + 0x60);
  param_2[6] = 0;
  if (param_4 == '\x05') {
    uVar1 = FUN_00454b88(param_1);
    *(undefined1 *)(param_2 + 3) = uVar1;
  }
  else if (param_1 == *DAT_0045605c) {
    *(undefined1 *)(param_2 + 3) = 0;
  }
  else {
    *(char *)(param_2 + 3) = param_4;
    if (param_4 == '\x03') {
      FUN_00454d7c();
      if (*(int *)(param_1 + 0x28) != 0) {
        *(undefined1 *)(param_2 + 3) = 2;
      }
      FUN_00454dcc();
    }
  }
  if (param_3 == 0) {
    *(undefined2 *)(param_2 + 8) = 0;
  }
  else {
    uVar2 = FUN_00455820(*(undefined4 *)(param_1 + 0x30));
    *(undefined2 *)(param_2 + 8) = uVar2;
  }
  return;
}

