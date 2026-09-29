
void FUN_00423864(undefined1 *param_1,undefined1 *param_2,uint param_3,undefined4 param_4)

{
  undefined1 uVar1;
  uint uVar2;
  undefined1 auStack_98 [128];
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  if (param_3 < 0x40) {
    for (; param_3 != 0; param_3 = param_3 - 1) {
      uVar1 = *param_1;
      *param_1 = *param_2;
      *param_2 = uVar1;
      param_1 = param_1 + 1;
      param_2 = param_2 + 1;
    }
    return;
  }
  do {
    uVar2 = 0x80;
    if (param_3 < 0x81) {
      uVar2 = param_3;
    }
    FUN_0041568c(auStack_98,param_1,uVar2);
    FUN_0041568c(param_1,param_2,uVar2);
    FUN_0041568c(param_2,auStack_98,uVar2);
    param_3 = param_3 - uVar2;
    param_1 = param_1 + uVar2;
    param_2 = param_2 + uVar2;
  } while (param_3 != 0);
  return;
}

