
undefined4 FUN_0058e2d8(int param_1,int param_2,uint param_3,uint *param_4)

{
  undefined4 uVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  uVar3 = 0;
  uVar1 = 0;
  iVar4 = *(int *)(param_1 + 0x28);
  while( true ) {
    if ((param_3 <= uVar3) || (*(int *)(DAT_0058e848 + iVar4 * 0x1000 + 0x18) << 0x1b < 0))
    goto LAB_0058e314;
    uVar2 = *(uint *)(DAT_0058e848 + iVar4 * 0x1000);
    if ((uVar2 & 0xf00) != 0) break;
    if (param_2 != 0) {
      *(char *)(param_2 + uVar3) = (char)uVar2;
      uVar3 = uVar3 + 1;
    }
  }
  uVar1 = 0x8000000;
LAB_0058e314:
  if (param_4 != (uint *)0x0) {
    *param_4 = uVar3;
  }
  return uVar1;
}

