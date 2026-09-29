
undefined4 FUN_0044c582(int param_1,int param_2)

{
  undefined1 uVar1;
  undefined4 uVar2;
  
  uVar2 = FUN_0044b8d0(param_1,param_2);
  uVar1 = FUN_0044b8de(param_1,param_2);
  uVar2 = FUN_00440fde(uVar2,uVar1);
  if (param_2 == 0) {
    param_1 = FUN_0044dca2(param_1);
  }
  for (; param_1 != 0; param_1 = FUN_0044dca2(param_1)) {
    uVar2 = FUN_0044c54a(param_1,0,uVar2);
  }
  return uVar2;
}

