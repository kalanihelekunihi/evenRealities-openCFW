
undefined8 FUN_005d6d98(undefined4 *param_1)

{
  uint uVar1;
  byte *pbVar2;
  undefined4 unaff_r7;
  
  if ((uint)param_1[3] < (uint)param_1[2]) {
    pbVar2 = (byte *)param_1[3];
    param_1[3] = pbVar2 + 1;
    uVar1 = (uint)*pbVar2;
  }
  else {
    FUN_005d2a0a(*param_1,0x55);
    uVar1 = 0;
  }
  return CONCAT44(unaff_r7,uVar1);
}

