
undefined4 FUN_0058e31e(int param_1,int param_2,uint param_3,uint *param_4)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = 0;
  iVar2 = *(int *)(param_1 + 0x28);
  while ((uVar1 < param_3 && (-1 < *(int *)(DAT_0058e848 + iVar2 * 0x1000 + 0x18) << 0x1a))) {
    *(uint *)(DAT_0058e848 + iVar2 * 0x1000) = (uint)*(byte *)(param_2 + uVar1);
    uVar1 = uVar1 + 1;
  }
  if (param_4 != (uint *)0x0) {
    *param_4 = uVar1;
  }
  return 0;
}

