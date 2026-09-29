
undefined8 FT_Stream_Skip(int param_1,int param_2)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (param_2 < 0) {
    uVar1 = 0x55;
  }
  else {
    uVar1 = FT_Stream_Seek(param_1,param_2 + *(int *)(param_1 + 8));
  }
  return CONCAT44(unaff_r7,uVar1);
}

