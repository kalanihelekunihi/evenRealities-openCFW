
undefined4 FUN_0050c3c0(void)

{
  undefined4 *puVar1;
  uint uVar2;
  undefined4 in_r3;
  
  puVar1 = DAT_0050c9b8;
  osMutexAcquire(*DAT_0050c9b8,0xffffffff);
  uVar2 = FUN_0050b1ac();
  osMutexRelease(*puVar1);
  *(uint *)(DAT_0050c97c + 0xc0) = uVar2 & 0xffff;
  return in_r3;
}

