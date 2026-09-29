
uint FUN_005444f4(undefined4 param_1,undefined4 param_2,int param_3,uint param_4,uint *param_5)

{
  int iVar1;
  uint uVar2;
  undefined1 auStack_70 [12];
  uint local_64;
  undefined4 local_1c;
  
  uVar2 = 0;
  iVar1 = FUN_0054449a(param_1,param_2,auStack_70);
  if (iVar1 == 0) {
    if (param_5 != (uint *)0x0) {
      *param_5 = 0;
    }
  }
  else {
    if (param_5 != (uint *)0x0) {
      *param_5 = local_64;
    }
    uVar2 = param_4;
    if (local_64 < param_4) {
      uVar2 = local_64;
    }
    if (param_3 != 0) {
      FUN_00585a12(param_1,local_1c,param_3,uVar2);
    }
  }
  return uVar2;
}

