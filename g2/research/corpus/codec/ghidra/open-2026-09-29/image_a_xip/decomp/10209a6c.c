
undefined4 gx8002_fixunsdfsi(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = gx8002_gedf2(param_1,param_2,0,0);
  if (iVar1 < 0) {
    uVar2 = gx8002_fixdfsi(param_1,param_2);
    return uVar2;
  }
  gx8002_subdf3(param_1,param_2,0,0);
  uVar2 = gx8002_fixdfsi();
  return uVar2;
}

