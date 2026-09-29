
undefined4 FUN_0058dae4(uint param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  uint *puVar3;
  
  iVar1 = DAT_0058e3f4;
  if (param_1 < 4) {
    if (param_2 == (int *)0x0) {
      uVar2 = 6;
    }
    else if ((*param_2 == 0) || ((*(uint *)*param_2 & 0x1ffffff) != DAT_0058e3f0)) {
      puVar3 = (uint *)(param_1 * 0x11c + DAT_0058e3f4);
      *puVar3 = *puVar3 | 0x1000000;
      puVar3 = (uint *)(iVar1 + param_1 * 0x11c);
      *puVar3 = *puVar3 & 0xff000000 | DAT_0058e440;
      *(uint *)(param_1 * 0x11c + iVar1 + 0x28) = param_1;
      *(undefined1 *)(param_1 * 0x11c + iVar1 + 4) = 0;
      *(undefined4 *)(param_1 * 0x11c + iVar1 + 0x30) = 0;
      *(undefined1 *)(param_1 * 0x11c + iVar1 + 0x11a) = 0;
      *(undefined1 *)(param_1 * 0x11c + iVar1 + 0x119) = 0;
      *(undefined1 *)(param_1 * 0x11c + iVar1 + 0xdc) = 0;
      *(undefined1 *)(param_1 * 0x11c + iVar1 + 0xdd) = 0;
      *(undefined4 *)(param_1 * 0x11c + iVar1 + 0xd8) = 0;
      *(undefined4 *)(param_1 * 0x11c + iVar1 + 0x9c) = 0;
      *(undefined1 *)(param_1 * 0x11c + iVar1 + 0xde) = 1;
      *param_2 = param_1 * 0x11c + iVar1;
      uVar2 = 0;
    }
    else {
      uVar2 = 7;
    }
  }
  else {
    uVar2 = 5;
  }
  return uVar2;
}

