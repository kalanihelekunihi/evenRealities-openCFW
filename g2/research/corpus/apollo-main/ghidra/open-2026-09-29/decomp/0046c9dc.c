
undefined8 FUN_0046c9dc(uint param_1,uint param_2)

{
  undefined4 uVar1;
  undefined4 unaff_r5;
  
  if ((param_1 < 0x31) && (param_2 < 0x41)) {
    *DAT_0046cabc = param_1;
    *DAT_0046cac0 = param_2;
    FUN_0047381e();
    unaff_r5 = 0x240;
    FUN_00474066(0,0,0,0,0x240,0x120);
    uVar1 = 0;
  }
  else {
    uVar1 = 0xffffffff;
  }
  return CONCAT44(unaff_r5,uVar1);
}

