
void prvTimerTask(void)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  undefined1 auStack_24 [4];
  int local_20;
  code *local_1c;
  int local_18;
  undefined4 local_14;
  
  puVar1 = DAT_0800b1f8;
  iVar2 = FUN_0800c83a(*DAT_0800b1f8,&local_20,0);
  do {
    if (iVar2 == 0) {
      return;
    }
    if (local_20 < 0) {
      (*local_1c)(local_18,local_14);
    }
    iVar2 = local_18;
    if (-1 < local_20) {
      if (*(int *)(local_18 + 0x14) != 0) {
        uxListRemove(local_18 + 4);
      }
      iVar3 = FUN_0800b284(auStack_24);
      switch(local_20) {
      case 0:
      case 1:
      case 2:
      case 6:
      case 7:
        *(byte *)(iVar2 + 0x28) = *(byte *)(iVar2 + 0x28) | 1;
        iVar3 = FUN_0800b024(iVar2,local_1c + *(int *)(iVar2 + 0x18),iVar3,local_1c);
        if (((iVar3 != 0) &&
            ((**(code **)(iVar2 + 0x20))(iVar2), (int)((uint)*(byte *)(iVar2 + 0x28) << 0x1d) < 0))
           && (iVar2 = FUN_0800cd80(iVar2,0,local_1c + *(int *)(iVar2 + 0x18),0,0), iVar2 == 0)) {
          disableIRQinterrupts();
          do {
                    /* WARNING: Do nothing block with infinite loop */
          } while( true );
        }
        break;
      case 3:
      case 8:
        *(byte *)(iVar2 + 0x28) = *(byte *)(iVar2 + 0x28) & 0xfe;
        break;
      case 4:
      case 9:
        *(byte *)(iVar2 + 0x28) = *(byte *)(iVar2 + 0x28) | 1;
        *(code **)(iVar2 + 0x18) = local_1c;
        if (local_1c == (code *)0x0) {
          disableIRQinterrupts();
          do {
                    /* WARNING: Do nothing block with infinite loop */
          } while( true );
        }
        FUN_0800b024(iVar2,local_1c + iVar3,iVar3,iVar3);
        break;
      case 5:
        if ((int)((uint)*(byte *)(iVar2 + 0x28) << 0x1e) < 0) {
          *(byte *)(iVar2 + 0x28) = *(byte *)(iVar2 + 0x28) & 0xfe;
        }
        else {
          FUN_0800c030(iVar2);
        }
      }
    }
    iVar2 = FUN_0800c83a(*puVar1,&local_20,0);
  } while( true );
}

