
undefined8 FT_Outline_Done(undefined4 *param_1)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (param_1 == (undefined4 *)0x0) {
    uVar1 = 0x21;
  }
  else {
    uVar1 = FT_Outline_Done_Internal(*param_1);
  }
  return CONCAT44(unaff_r7,uVar1);
}

