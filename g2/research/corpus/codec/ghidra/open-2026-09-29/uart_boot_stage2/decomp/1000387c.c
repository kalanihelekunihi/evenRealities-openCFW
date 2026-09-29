
undefined4 FUN_1000387c(void)

{
  byte bStack_5;
  
  FUN_100034a4(0x35,&bStack_5,1);
  if ((bStack_5 & 2) == 0) {
    bStack_5 = bStack_5 | 2;
    FUN_100035a8(&bStack_5,1,2);
    FUN_1000385c();
  }
  return 0;
}

