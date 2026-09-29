
void FUN_004238ba(undefined1 *param_1,undefined1 *param_2,undefined1 *param_3,uint param_4)

{
  undefined1 uVar1;
  uint uVar2;
  undefined1 auStack_98 [128];
  
  if (param_4 < 0x40) {
    for (; param_4 != 0; param_4 = param_4 - 1) {
      uVar1 = *param_1;
      *param_1 = *param_3;
      *param_3 = *param_2;
      *param_2 = uVar1;
      param_1 = param_1 + 1;
      param_2 = param_2 + 1;
      param_3 = param_3 + 1;
    }
  }
  else {
    do {
      uVar2 = 0x80;
      if (param_4 < 0x81) {
        uVar2 = param_4;
      }
      FUN_0041568c(auStack_98,param_1,uVar2);
      FUN_0041568c(param_1,param_3,uVar2);
      FUN_0041568c(param_3,param_2,uVar2);
      FUN_0041568c(param_2,auStack_98,uVar2);
      param_4 = param_4 - uVar2;
      param_1 = param_1 + uVar2;
      param_2 = param_2 + uVar2;
      param_3 = param_3 + uVar2;
    } while (param_4 != 0);
  }
  return;
}

