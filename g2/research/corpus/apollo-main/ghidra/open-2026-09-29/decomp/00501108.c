
undefined1 *
FUN_00501108(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
            undefined4 param_5,undefined4 param_6,undefined4 param_7)

{
  undefined1 *puVar1;
  
  puVar1 = DAT_00501170;
  FUN_0043c0e4(DAT_00501170,0x1024,0);
  *puVar1 = 6;
  *(undefined4 *)(puVar1 + 4) = param_1;
  *(undefined2 *)(puVar1 + 8) = 9;
  *(undefined4 *)(puVar1 + 0xc) = param_2;
  *(undefined4 *)(puVar1 + 0x10) = param_3;
  *(undefined4 *)(puVar1 + 0x14) = param_4;
  *(undefined4 *)(puVar1 + 0x18) = param_5;
  *(undefined4 *)(puVar1 + 0x1c) = param_6;
  *(undefined4 *)(puVar1 + 0x20) = param_7;
  FUN_00500a02();
  return puVar1;
}

