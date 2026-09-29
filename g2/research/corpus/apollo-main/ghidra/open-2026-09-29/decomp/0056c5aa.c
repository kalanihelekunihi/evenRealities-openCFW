
undefined8 attsUuid16Cmp(char *param_1,char param_2,char *param_3)

{
  byte bVar1;
  uint uVar2;
  undefined4 unaff_r7;
  
  if (param_2 == '\x02') {
    if ((*param_1 == *param_3) && (param_1[1] == param_3[1])) {
      bVar1 = 1;
    }
    else {
      bVar1 = 0;
    }
    uVar2 = (uint)bVar1;
  }
  else {
    uVar2 = attUuidCmp16to128(param_1,param_3);
  }
  return CONCAT44(unaff_r7,uVar2);
}

