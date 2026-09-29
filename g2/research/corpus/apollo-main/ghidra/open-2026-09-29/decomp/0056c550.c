
undefined8 attsUuidCmp(undefined4 *param_1,char param_2,undefined4 param_3)

{
  int iVar1;
  uint uVar2;
  undefined4 unaff_r7;
  
  if ((((int)((uint)*(byte *)((int)param_1 + 0xe) << 0x1f) < 0) || (param_2 != '\x02')) &&
     ((-1 < (int)((uint)*(byte *)((int)param_1 + 0xe) << 0x1f) || (param_2 != '\x10')))) {
    if (((int)((uint)*(byte *)((int)param_1 + 0xe) << 0x1f) < 0) || (param_2 != '\x10')) {
      uVar2 = attUuidCmp16to128(param_3,*param_1);
    }
    else {
      uVar2 = attUuidCmp16to128(*param_1,param_3);
    }
  }
  else {
    iVar1 = FUN_004751c8(*param_1,param_3,param_2);
    uVar2 = (uint)(iVar1 == 0);
  }
  return CONCAT44(unaff_r7,uVar2);
}

