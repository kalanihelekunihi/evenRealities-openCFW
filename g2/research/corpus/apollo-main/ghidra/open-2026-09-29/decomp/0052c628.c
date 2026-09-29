
undefined8 AttsCccEnabled(undefined1 param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  undefined4 uVar2;
  
  bVar1 = DmConnSecLevel(param_1);
  if (bVar1 < *(byte *)(*(int *)(DAT_0052c674 + 0xc) + (uint)param_2 * 6 + 4)) {
    uVar2 = 0;
  }
  else {
    uVar2 = AttsCccGet(param_1,param_2);
  }
  return CONCAT44(param_4,uVar2);
}

