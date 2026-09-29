
undefined8 FUN_005e54a2(undefined1 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  char cVar2;
  undefined4 uVar3;
  
  if (((param_2 & 0xff) == 1) || ((param_2 & 0xff) == 2)) {
    FUN_005e583c(param_1,0);
    uVar3 = 8;
  }
  else {
    uVar1 = UX_GetSystemBLEStatus();
    cVar2 = FUN_005e50ea(uVar1);
    if (cVar2 == '\x02') {
      FUN_005e522e(param_1,param_2);
      uVar3 = 4;
    }
    else if (cVar2 == '\x03') {
      FUN_005e5290(param_1,param_2);
      uVar3 = 4;
    }
    else if (cVar2 == '\x04') {
      FUN_005e52c2(param_1,param_2);
      uVar3 = 4;
    }
    else if (cVar2 == '\x16') {
      FUN_005e6548(param_1,*(undefined4 *)(DAT_005e5dd8 + 0x288));
      uVar3 = 0xb;
    }
    else if (cVar2 == '\a') {
      FUN_005e641c(param_1,1);
      uVar3 = 10;
    }
    else {
      FUN_005e57c6(param_1,param_2);
      uVar3 = 3;
    }
  }
  return CONCAT44(param_4,uVar3);
}

