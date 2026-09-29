
undefined4 FUN_100038b8(void)

{
  byte bStack_9;
  undefined1 uStack_8;
  byte bStack_7;
  
  FUN_100034a4(5,&uStack_8,1);
  FUN_100034a4(0x35,&bStack_9,1);
  if ((bStack_9 & 2) == 0) {
    bStack_7 = bStack_9 | 2;
    FUN_100035a8(&uStack_8,2,1);
    FUN_1000385c();
  }
  return 0;
}

