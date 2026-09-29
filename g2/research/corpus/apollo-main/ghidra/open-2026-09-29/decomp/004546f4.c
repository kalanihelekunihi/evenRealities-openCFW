
void FUN_004546f4(undefined4 param_1)

{
  byte bVar1;
  
  bVar1 = FUN_004546d0(param_1,0);
  if ((bVar1 != 0) && ((uint)bVar1 <= *(uint *)(DAT_00454734 + 0x58))) {
    (**(code **)(*(int *)(DAT_00454734 + 0x5c) + (uint)bVar1 * 8))
              (param_1,*(undefined4 *)(*(int *)(DAT_00454734 + 0x5c) + (uint)bVar1 * 8 + 4));
  }
  return;
}

