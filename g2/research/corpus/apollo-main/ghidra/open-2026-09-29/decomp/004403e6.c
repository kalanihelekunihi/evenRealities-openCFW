
void FUN_004403e6(int param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  char cVar1;
  undefined4 uVar2;
  uint uVar3;
  
  if (param_1 != 0) {
    cVar1 = FUN_00452dd8(param_1);
    uVar3 = (param_4 & 0xff) >> 1 & 1;
    if (uVar3 == 0) {
      if (cVar1 == '\x02') {
        FUN_00440dda(param_1,param_2,param_3,0);
      }
      if ((param_4 & 1) != 0) {
        uVar2 = FUN_0044dca2(param_1);
        FUN_004403e6(uVar2,param_2,param_3,param_4 & 0xff);
      }
    }
    else {
      if ((param_4 & 1) != 0) {
        uVar2 = FUN_0044dca2(param_1);
        FUN_004403e6(uVar2,param_2,param_3,param_4 & 0xff);
      }
      if (cVar1 == '\x02') {
        FUN_00440dda(param_1,param_2,param_3,uVar3);
      }
    }
  }
  return;
}

