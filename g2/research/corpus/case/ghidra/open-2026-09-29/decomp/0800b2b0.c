
void FUN_0800b2b0(void)

{
  int iVar1;
  int iVar2;
  uint *puVar3;
  uint uVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  
  iVar1 = DAT_0800b318;
  iVar2 = **(int **)(DAT_0800b318 + 0xc);
  do {
    if (iVar2 == 0) {
      uVar5 = *(undefined4 *)(iVar1 + 0xc);
      *(undefined4 *)(iVar1 + 0xc) = *(undefined4 *)(iVar1 + 0x10);
      *(undefined4 *)(iVar1 + 0x10) = uVar5;
      return;
    }
    puVar3 = *(uint **)(*(int *)(iVar1 + 0xc) + 0xc);
    uVar7 = *puVar3;
    uVar6 = puVar3[3];
    uxListRemove(uVar6 + 4);
    (**(code **)(uVar6 + 0x20))(uVar6);
    if ((int)((uint)*(byte *)(uVar6 + 0x28) << 0x1d) < 0) {
      uVar4 = *(int *)(uVar6 + 0x18) + uVar7;
      if (uVar7 < uVar4) {
        *(uint *)(uVar6 + 4) = uVar4;
        *(uint *)(uVar6 + 0x10) = uVar6;
        FUN_0800bfb0(*(undefined4 *)(iVar1 + 0xc),uVar6 + 4);
      }
      else {
        iVar2 = FUN_0800cd80(uVar6,0,uVar7,0,0);
        if (iVar2 == 0) {
          disableIRQinterrupts();
          do {
                    /* WARNING: Do nothing block with infinite loop */
          } while( true );
        }
      }
    }
    iVar2 = **(int **)(iVar1 + 0xc);
  } while( true );
}

