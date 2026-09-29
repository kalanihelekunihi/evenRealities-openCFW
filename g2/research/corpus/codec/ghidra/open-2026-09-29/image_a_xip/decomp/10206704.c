
undefined4 gx8002_watchdog_interrupt(void)

{
  undefined4 uVar1;
  
  if (*puRam1020671c == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = (*(code *)(*puRam1020671c & 0xfffffffe))();
  }
  return uVar1;
}

