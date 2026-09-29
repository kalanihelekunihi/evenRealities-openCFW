
void FUN_00500bf4(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  
  uVar4 = (uint)(param_1 == '\0');
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uVar3 = DAT_005017ac;
    if (param_1 != '\0') {
      uVar3 = DAT_005017a8;
    }
    FUN_0043d574(3,DAT_00501188,DAT_00501184,DAT_005017b4,0x142,DAT_005017b0,*DAT_005017a4,uVar4,
                 uVar3,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    uVar3 = DAT_005017ac;
    if (param_1 != '\0') {
      uVar3 = DAT_005017a8;
    }
    compress_log_output(0xcc00000,DAT_005017b8,DAT_005017b8,*DAT_005017a4,uVar4,uVar3);
  }
  puVar1 = DAT_00501170;
  FUN_0043c0e4(DAT_00501170,0x1024,0);
  *puVar1 = 7;
  *(undefined4 *)(puVar1 + 4) = *DAT_005017a4;
  *(undefined2 *)(puVar1 + 8) = 10;
  *(uint *)(puVar1 + 0xc) = uVar4;
  FUN_00500a0c();
  return;
}

