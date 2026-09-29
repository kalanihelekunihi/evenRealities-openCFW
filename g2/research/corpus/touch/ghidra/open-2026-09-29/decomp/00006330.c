
undefined4 touch_sub_3030(void)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = touch_sub_2f70();
  if (uVar1 < 0x10) {
    if (uVar1 < 8) {
      if (uVar1 < 4) {
        uVar2 = 0;
      }
      else {
        uVar2 = 1;
      }
    }
    else {
      uVar2 = 2;
    }
  }
  else {
    uVar2 = 3;
  }
  return uVar2;
}

