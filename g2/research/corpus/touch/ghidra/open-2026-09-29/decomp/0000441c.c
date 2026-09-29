
char proximity_baseline_update_adapter(void)

{
  ushort uVar1;
  int iVar2;
  uint uVar3;
  ushort *puVar4;
  char cVar5;
  uint uVar6;
  
  iVar2 = capsense_sensor_raw_count_read(2,0,DAT_00004478);
  if (iVar2 == 0) {
    cVar5 = '\x01';
  }
  else {
    cVar5 = '\x02';
  }
  puVar4 = *(ushort **)(*(int *)(DAT_00004478 + 0xc) + 0x124);
  uVar6 = (uint)puVar4[1];
  uVar1 = *puVar4;
  uVar3 = saved_proximity_baseline_read();
  if (uVar3 != 0) {
    if ((int)(uVar3 + 500) < (int)uVar6) {
      cVar5 = '\x02';
    }
    else if ((uVar6 < uVar3) && ((int)(uint)uVar1 <= (int)(uVar3 + 0x31))) {
      cVar5 = '\x01';
    }
  }
  if (*DAT_0000447c == cVar5) {
    cVar5 = '\0';
  }
  else {
    *DAT_0000447c = cVar5;
  }
  return cVar5;
}

