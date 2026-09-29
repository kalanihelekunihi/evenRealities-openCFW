
undefined8 FUN_005b3f94(undefined4 param_1,uint param_2,uint param_3)

{
  ushort uVar1;
  uint uVar2;
  undefined2 uVar3;
  
  if ((param_2 & 0xffff) == 0) {
    uVar2 = 0;
    param_3 = param_2;
  }
  else {
    uVar2 = FUN_004897fc(param_1,param_2 & 0xffff,*DAT_005b4848,0,param_3,0,0);
    if (uVar2 == 0) {
      if ((param_2 & 0xffff) < 4) {
        uVar3 = (undefined2)param_2;
      }
      else {
        uVar3 = 4;
      }
      uVar1 = FUN_005b3ef8(param_1,uVar3);
      if ((uVar1 == 0) && ((param_2 & 0xffff) != 0)) {
        uVar1 = 1;
      }
      uVar2 = (uint)uVar1;
    }
    else {
      if ((param_2 & 0xffff) < uVar2) {
        uVar2 = param_2 & 0xffff;
      }
      uVar2 = uVar2 & 0xffff;
    }
  }
  return CONCAT44(param_3,uVar2);
}

