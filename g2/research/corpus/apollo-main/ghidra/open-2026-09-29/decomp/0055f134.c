
undefined8 FUN_0055f134(int *param_1,uint param_2)

{
  undefined4 uVar1;
  uint unaff_r7;
  
  uVar1 = DAT_0055f2ac;
  if (((param_2 & 0xffff) - 0x20 < 0x301) && (-1 < (int)(param_2 << 0x1f))) {
    unaff_r7 = CONCAT22((short)(unaff_r7 >> 0x10),
                        CONCAT11((char)((param_2 & 0xffff) >> 1),(char)((param_2 & 0xffff) >> 2))) &
               0xffff01ff;
    *(short *)(param_1 + 1) = (short)param_2;
    uVar1 = FUN_0055fc2c(*(undefined4 *)(*param_1 + 4),0x308,&stack0xfffffff8,2);
  }
  return CONCAT44(unaff_r7,uVar1);
}

