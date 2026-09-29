
void report_builder(void)

{
  undefined2 uVar1;
  ushort uVar2;
  undefined2 uVar3;
  ushort uVar4;
  undefined4 *puVar5;
  undefined1 uVar6;
  undefined2 uVar7;
  undefined4 *puVar8;
  int iVar9;
  char *pcVar10;
  char cVar11;
  undefined2 *puVar12;
  ushort uVar13;
  undefined4 uVar14;
  undefined4 uVar15;
  
  iVar9 = DAT_00003c60;
  uVar6 = capsense_widget_active_query(1,DAT_00003c60);
  puVar8 = (undefined4 *)capsense_widget_data_pointer(1,iVar9);
  puVar5 = DAT_00003c64;
  uVar1 = *(undefined2 *)*puVar8;
  iVar9 = proximity_baseline_update_adapter(*DAT_00003c64);
  pcVar10 = (char *)touch_gesture_state_machine(DAT_00003c68,uVar6,(char)uVar1,*puVar5);
  puVar5 = DAT_00003c6c;
  if (iVar9 == 0) {
    if (pcVar10 == (char *)0x0) {
      return;
    }
    if (*pcVar10 == '\0') {
      return;
    }
    *(undefined1 *)DAT_00003c6c = 0;
  }
  else {
    *(char *)DAT_00003c6c = (char)iVar9;
    if (pcVar10 == (char *)0x0) {
      cVar11 = '\0';
      *(undefined1 *)((int)puVar5 + 1) = 0;
      *(undefined1 *)((int)puVar5 + 2) = 0;
      goto LAB_00003b86;
    }
  }
  puVar5 = DAT_00003c6c;
  *(char *)((int)DAT_00003c6c + 1) = *pcVar10;
  *(char *)((int)puVar5 + 2) = pcVar10[1];
  cVar11 = pcVar10[2];
LAB_00003b86:
  *(char *)((int)DAT_00003c6c + 3) = cVar11;
  puVar12 = *(undefined2 **)(*(int *)(DAT_00003c60 + 0xc) + 0x124);
  uVar2 = puVar12[1];
  uVar1 = *puVar12;
  uVar3 = puVar12[2];
  uVar7 = saved_proximity_baseline_read();
  if (*DAT_00003c70 != '\0') {
    uVar4 = *(ushort *)(DAT_00003c74 + 4);
    if (uVar4 < uVar2) {
      uVar13 = uVar2 - uVar4;
    }
    else {
      uVar13 = uVar4 - uVar2;
    }
    if (uVar13 < 0x32) {
      logger_stub(DAT_00003c84,uVar4,uVar2,uVar13,0x32,DAT_00003c7c);
    }
    else {
      *(ushort *)(DAT_00003c74 + 4) = uVar2;
      iVar9 = touch_config_load_from_eeprom();
      if (iVar9 == 0) {
        logger_stub(DAT_00003c78,uVar4,uVar2,uVar13,DAT_00003c7c);
      }
      else {
        logger_stub(DAT_00003c80,iVar9,DAT_00003c7c);
      }
    }
    *DAT_00003c70 = '\0';
  }
  puVar5 = DAT_00003c6c;
  *(ushort *)(DAT_00003c6c + 1) = uVar2;
  *(undefined2 *)((int)puVar5 + 6) = uVar1;
  *(undefined2 *)(puVar5 + 2) = uVar3;
  *(undefined2 *)((int)puVar5 + 10) = uVar7;
  puVar8 = DAT_00003c88;
  uVar14 = puVar5[1];
  uVar15 = puVar5[2];
  *DAT_00003c88 = *puVar5;
  puVar8[1] = uVar14;
  puVar8[2] = uVar15;
  puVar8[3] = puVar5[3];
  i2c_tx_descriptor_arm(DAT_00003c90,puVar8,0x10,DAT_00003c8c);
  *(undefined4 *)(DAT_00003c94 + 0x44) = 1;
  logger_stub(DAT_00003c98,*(undefined1 *)puVar5,*(undefined1 *)((int)puVar5 + 1),
              *(undefined1 *)((int)puVar5 + 2),*(undefined1 *)((int)puVar5 + 3),DAT_00003c7c);
  *DAT_00003c9c = 1;
  *DAT_00003ca0 = 0x280;
  return;
}

