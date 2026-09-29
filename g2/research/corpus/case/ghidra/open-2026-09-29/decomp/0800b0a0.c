
void FUN_0800b0a0(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = *(int *)(*(int *)(*(int *)(DAT_0800b0f8 + 0xc) + 0xc) + 0xc);
  uxListRemove(iVar2 + 4);
  if ((int)((uint)*(byte *)(iVar2 + 0x28) << 0x1d) < 0) {
    iVar1 = FUN_0800b024(iVar2,*(int *)(iVar2 + 0x18) + param_1,param_2,param_1,param_4);
    if (iVar1 != 0) {
      iVar1 = FUN_0800cd80(iVar2,0,param_1,0,0);
      if (iVar1 == 0) {
        disableIRQinterrupts();
        do {
                    /* WARNING: Do nothing block with infinite loop */
        } while( true );
      }
    }
  }
  else {
    *(byte *)(iVar2 + 0x28) = *(byte *)(iVar2 + 0x28) & 0xfe;
  }
  (**(code **)(iVar2 + 0x20))(iVar2);
  return;
}

