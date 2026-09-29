
undefined8 FUN_005445b2(undefined4 param_1,int param_2,int param_3)

{
  byte bVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  bVar1 = FUN_005858d8(param_1,param_2,param_3,6,1,0);
  if (bVar1 == 0) {
    uVar2 = 0;
    bVar1 = FUN_00585a52(param_1,param_2 + 4,param_3 + 4,0x14);
  }
  return CONCAT44(uVar2,(uint)bVar1);
}

