
void FUN_004c8f0a(void)

{
  undefined1 *puVar1;
  
  puVar1 = DAT_004c9188;
  FUN_004c7064(DAT_004c9188);
  *puVar1 = 0x4c;
  *(undefined4 *)(puVar1 + 0xc) = 0x4c8f59;
  *(undefined4 *)(puVar1 + 0x10) = 0x4c8fd9;
  *(undefined1 **)(puVar1 + 0x14) = &LAB_004c8ff0_1;
  *(undefined1 **)(puVar1 + 0x18) = &LAB_004c900c_1;
  *(undefined1 **)(puVar1 + 0x1c) = &LAB_004c9028_1;
  *(undefined1 **)(puVar1 + 0x20) = &LAB_004c9064_1;
  *(undefined4 *)(puVar1 + 0x24) = 0x4c9081;
  *(undefined1 **)(puVar1 + 0x2c) = &LAB_004c90e4_1;
  *(undefined4 *)(puVar1 + 0x28) = 0x4c9105;
  FUN_004c706e(puVar1);
  return;
}

