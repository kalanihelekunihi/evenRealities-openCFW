
undefined4 TimerCallback(void)

{
  uint uVar1;
  undefined4 *puVar2;
  undefined4 unaff_r7;
  
  uVar1 = FUN_0047eb26();
  puVar2 = (undefined4 *)(uVar1 & 0xfffffffe);
  if (puVar2 != (undefined4 *)0x0) {
    (*(code *)*puVar2)(puVar2[1]);
  }
  return unaff_r7;
}

