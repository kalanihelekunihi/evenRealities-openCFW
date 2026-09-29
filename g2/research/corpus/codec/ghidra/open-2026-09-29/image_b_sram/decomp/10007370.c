
undefined4 FUN_10007370(void)

{
  byte bStack_9;
  undefined1 uStack_8;
  byte bStack_7;
  
  FUN_10006c30(5,&uStack_8,1);
  FUN_10006c30(0x35,&bStack_9,1);
  if ((bStack_9 & 2) == 0) {
    bStack_7 = bStack_9 | 2;
    FUN_10006d34(&uStack_8,2,1);
    FUN_10007350();
  }
  return 0;
}

