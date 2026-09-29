
undefined8 FUN_0047f3c6(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  uint *puVar1;
  undefined4 uVar2;
  uint uVar3;
  uint local_10;
  undefined4 uStack_c;
  
  puVar1 = DAT_0047fad4;
  local_10 = param_3;
  if (*DAT_0047fad0 == '\x01') {
    local_10 = *DAT_0047fad4 | 0x80;
    uStack_c = param_4;
    FUN_00480312(5,1,&local_10);
    *DAT_0047fadc = *DAT_0047fadc | 0x20;
    uVar3 = 0;
    while ((uVar3 < 10000 && (-1 < (int)(*puVar1 << 0x18)))) {
      uVar3 = uVar3 + 1;
    }
    if (uVar3 == 10000) {
      uVar2 = 4;
      goto LAB_0047f416;
    }
  }
  uVar2 = 0;
LAB_0047f416:
  return CONCAT44(local_10,uVar2);
}

