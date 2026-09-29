
void FUN_00514d98(undefined4 *param_1)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  if (param_1 == (undefined4 *)0x0) {
    FUN_0051565c(1);
    return;
  }
  FUN_00561810(param_1 + 0x18);
  param_1[0x21] = 0;
  if (param_1 != (undefined4 *)0x0) {
    param_1[2] = 0;
    param_1[3] = 0;
    *param_1 = 0;
    uVar2 = DAT_00514f38;
    uVar1 = DAT_00514f34;
    param_1[1] = 0;
    param_1[4] = uVar1;
    param_1[5] = uVar1;
    param_1[6] = uVar2;
    param_1[7] = uVar2;
    param_1[0x14] = 0;
    param_1[0x15] = 0;
    param_1[9] = 0;
    param_1[8] = 0;
    param_1[0xb] = 0;
    param_1[10] = 0;
    param_1[0xd] = 0;
    param_1[0xc] = 0;
    param_1[0xf] = 0;
    param_1[0xe] = 0;
    param_1[0x16] = 0;
    param_1[0x17] = 0;
    param_1[0x10] = uVar1;
    param_1[0x11] = uVar1;
    param_1[0x12] = uVar2;
    param_1[0x13] = uVar2;
  }
  FUN_00514178(param_1);
  return;
}

