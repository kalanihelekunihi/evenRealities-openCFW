
undefined4 FUN_004848b2(int param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 *puVar2;
  undefined1 auStack_20 [16];
  undefined4 uStack_10;
  
  puVar2 = *(undefined4 **)(param_1 + 0x44);
  uStack_10 = param_4;
  while( true ) {
    if ((puVar2 == (undefined4 *)0x0) || (puVar2 == param_2)) {
      return 1;
    }
    if ((puVar2[0x14] != 3) && (iVar1 = FUN_00450bcc(auStack_20,puVar2 + 6,param_2 + 6), iVar1 != 0)
       ) break;
    puVar2 = (undefined4 *)*puVar2;
  }
  return 0;
}

