
void FUN_005823f6(undefined1 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  char *pcVar2;
  
  puVar1 = DAT_00582890;
  FUN_0043c0e4(DAT_00582890,0xf58,0,param_4,param_4);
  *puVar1 = 1;
  pcVar2 = DAT_00582894;
  *DAT_00582894 = *DAT_00582894 + '\x01';
  puVar1[1] = *pcVar2;
  *(undefined2 *)(puVar1 + 2) = 3;
  puVar1[4] = param_1;
  if (param_2 != 0) {
    puVar1[5] = 1;
    FUN_00439c04(puVar1 + 8,param_2,0x2c);
  }
  FUN_0058237a(puVar1);
  return;
}

