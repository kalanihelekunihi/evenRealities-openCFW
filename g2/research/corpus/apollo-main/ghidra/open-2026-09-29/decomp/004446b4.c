
void FUN_004446b4(void)

{
  undefined2 *puVar1;
  
  puVar1 = DAT_004448c0;
  FUN_00471cae(DAT_004448c0);
  *puVar1 = 1;
  *(undefined1 *)(puVar1 + 1) = 2;
  *(undefined4 *)(puVar1 + 6) = 0;
  *(undefined4 *)(puVar1 + 8) = 6000;
  FUN_00471c9a(0,puVar1);
  FUN_00471dac(0);
  FUN_00471e92(1);
  FUN_00442256(0x43,4);
  FUN_00442238(0x43);
  FUN_00473934();
  FUN_00471d58(0);
  return;
}

