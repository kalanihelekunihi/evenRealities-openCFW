
undefined4 FUN_100073f0(void)

{
  byte bStack_5;
  
  FUN_10006c30(0x15,&bStack_5,1);
  if ((bStack_5 & 0x10) == 0) {
    bStack_5 = bStack_5 | 0x10;
    FUN_10006d34(&bStack_5,1);
    FUN_10007350();
  }
  return 0;
}

