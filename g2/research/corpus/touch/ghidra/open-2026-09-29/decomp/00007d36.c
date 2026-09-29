
undefined1 capsense_sensor_raw_count_read(uint param_1,uint param_2,int param_3)

{
  undefined1 uVar1;
  int iVar2;
  
  if (param_1 < 3) {
    iVar2 = *(int *)(param_3 + 0xc) + param_1 * 0x90;
    if (*(char *)(iVar2 + 0x7b) == '\x06') {
      if (param_2 < *(ushort *)(iVar2 + 0x38)) {
        uVar1 = *(undefined1 *)(*(int *)(iVar2 + 4) + param_2 * 10 + 6);
      }
      else {
        uVar1 = 0;
      }
    }
    else {
      uVar1 = 0;
    }
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

