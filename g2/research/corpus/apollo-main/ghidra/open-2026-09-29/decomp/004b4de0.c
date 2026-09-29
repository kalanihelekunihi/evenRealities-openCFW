
undefined4 attL2cDataCback(undefined2 param_1,undefined2 param_2,int param_3)

{
  undefined4 unaff_r7;
  
  if ((int)((uint)*(byte *)(param_3 + 8) << 0x1f) < 0) {
    (*(code *)**(undefined4 **)(DAT_004b51d0 + 0x3c))(param_1,param_2);
  }
  else {
    (*(code *)**(undefined4 **)(DAT_004b51d0 + 0x40))(param_1,param_2);
  }
  return unaff_r7;
}

