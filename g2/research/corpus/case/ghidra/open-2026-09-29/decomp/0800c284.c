
void FUN_0800c284(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  
  local_10 = 0;
  local_14 = 0;
  FUN_0800bf54(&local_10,&local_14,&local_18);
  iVar2 = FUN_0800ca06(DAT_0800c2f0,&DAT_0800c2e8,local_18,0,0,local_14,local_10);
  iVar1 = DAT_0800c2f4;
  *(int *)(DAT_0800c2f4 + 0x2c) = iVar2;
  uVar3 = (uint)(iVar2 != 0);
  if (uVar3 == 1) {
    uVar3 = FUN_0800cd20();
  }
  if (uVar3 == 1) {
    disableIRQinterrupts();
    *(undefined4 *)(iVar1 + 0x28) = 0xffffffff;
    *(undefined4 *)(iVar1 + 0x14) = 1;
    *(undefined4 *)(iVar1 + 0xc) = 0;
    FUN_0800c57c();
  }
  else if (uVar3 == 0xffffffff) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  return;
}

