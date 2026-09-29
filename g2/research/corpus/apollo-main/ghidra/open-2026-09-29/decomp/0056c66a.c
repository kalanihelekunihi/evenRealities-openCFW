
undefined8 attsPermissions(undefined1 param_1,uint param_2,undefined2 param_3,uint param_4)

{
  byte bVar1;
  uint uVar2;
  
  if ((param_4 & 0xff & param_2) == 0) {
    if ((param_2 & 0xff) == 1) {
      bVar1 = 2;
    }
    else {
      bVar1 = 3;
    }
    uVar2 = (uint)bVar1;
  }
  else {
    uVar2 = param_4;
    if ((param_2 & 0xff) == 0x10) {
      uVar2 = (param_4 & 0xff) >> 4;
    }
    if ((uVar2 & 0xe) == 0) {
      uVar2 = 0;
    }
    else {
      bVar1 = DmConnSecLevel(param_1);
      if (((int)(uVar2 << 0x1c) < 0) && (bVar1 == 0)) {
        uVar2 = 5;
      }
      else if (((uVar2 & 10) == 10) && (bVar1 < 2)) {
        uVar2 = 5;
      }
      else if ((int)(uVar2 << 0x1d) < 0) {
        if (*(int *)(DAT_0056cd98 + 0x268) == 0) {
          uVar2 = 8;
        }
        else {
          uVar2 = (**(code **)(DAT_0056cd98 + 0x268))(param_1,param_2 & 0xff,param_3);
        }
      }
      else {
        uVar2 = 0;
      }
    }
  }
  return CONCAT44(param_4,uVar2);
}

