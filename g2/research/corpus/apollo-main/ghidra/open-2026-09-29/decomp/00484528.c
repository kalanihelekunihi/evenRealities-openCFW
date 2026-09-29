
void FUN_00484528(void)

{
  undefined4 *puVar1;
  
  for (puVar1 = *(undefined4 **)(DAT_004849a8 + 0x13c); puVar1 != (undefined4 *)0x0;
      puVar1 = (undefined4 *)*puVar1) {
    if (puVar1[5] != 0) {
      (*(code *)puVar1[5])(puVar1);
    }
  }
  return;
}

