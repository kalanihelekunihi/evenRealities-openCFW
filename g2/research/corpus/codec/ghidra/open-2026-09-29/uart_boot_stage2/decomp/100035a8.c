
uint FUN_100035a8(undefined4 param_1,uint param_2,int param_3)

{
  uint uVar1;
  undefined4 uVar2;
  byte bStack_15;
  
  if (2 < param_2) {
    return 0xffffffff;
  }
  if (param_3 == 2) {
    uVar2 = 0x31;
  }
  else if (param_3 == 3) {
    uVar2 = 0x11;
  }
  else {
    if (param_3 != 1) {
      return 0xffffffff;
    }
    uVar2 = 1;
  }
  do {
    FUN_100034a4(5,&bStack_15,1);
    uVar1 = bStack_15 & 1;
  } while ((bStack_15 & 1) != 0);
  FUN_10003524(6,uVar1,uVar1);
  FUN_10003524(uVar2,param_1,param_2);
  return uVar1;
}

