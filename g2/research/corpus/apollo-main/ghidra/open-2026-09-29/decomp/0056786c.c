
void FUN_0056786c(int param_1,int param_2,uint param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  undefined1 auStack_a0 [128];
  undefined4 uStack_20;
  
  uStack_20 = param_4;
  for (uVar1 = param_3; uVar1 != 0; uVar1 = uVar1 - uVar2) {
    uVar2 = 0x80;
    if (uVar1 < 0x81) {
      uVar2 = uVar1;
    }
    FUN_00439be4(auStack_a0,(param_3 - uVar2) + param_2,uVar2);
    FUN_00439710(param_1 + uVar2,param_1,((param_2 - param_1) + param_3) - uVar2);
    FUN_00439be4(param_1,auStack_a0,uVar2);
  }
  return;
}

