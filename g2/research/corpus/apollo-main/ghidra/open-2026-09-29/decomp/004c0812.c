
undefined4 FUN_004c0812(uint param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  uint *puVar3;
  
  iVar1 = DAT_004c0f64;
  if (param_1 < 4) {
    if (param_2 == (int *)0x0) {
      uVar2 = 6;
    }
    else if (*(int *)(DAT_004c0f64 + param_1 * 0x8d0) << 7 < 0) {
      uVar2 = 7;
    }
    else {
      puVar3 = (uint *)(param_1 * 0x8d0 + DAT_004c0f64);
      *puVar3 = *puVar3 | 0x1000000;
      puVar3 = (uint *)(param_1 * 0x8d0 + iVar1);
      *puVar3 = *puVar3 & 0xff000000 | 0xbebebe;
      *(uint *)(param_1 * 0x8d0 + iVar1 + 4) = param_1;
      *(undefined1 *)(param_1 * 0x8d0 + iVar1 + 0xc) = 0;
      *(undefined4 *)(param_1 * 0x8d0 + iVar1 + 0x18) = 0;
      *(undefined1 *)(param_1 * 0x8d0 + iVar1 + 0x8c9) = 7;
      *(undefined4 *)(param_1 * 0x8d0 + iVar1 + 0x8cc) = 8;
      *param_2 = param_1 * 0x8d0 + iVar1;
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 5;
  }
  return uVar2;
}

