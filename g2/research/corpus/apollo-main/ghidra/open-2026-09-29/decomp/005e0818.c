
undefined8 FUN_005e0818(int *param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  ushort uVar2;
  int iVar3;
  uint *puVar4;
  
  iVar3 = 0;
  puVar4 = (uint *)param_1[2];
  if ((char)param_1[4] == '\0') {
    iVar3 = 6;
  }
  else {
    uVar2 = *(ushort *)param_1[3];
    puVar4[1] = (uint)*(ushort *)(param_1[3] + 2);
    *puVar4 = (uint)uVar2;
    cVar1 = *(char *)((int)param_1 + 0x12);
    if (cVar1 == '\x01') {
      *(undefined1 *)((int)puVar4 + 0x12) = 1;
      puVar4[2] = puVar4[1] + 7 >> 3;
      *(undefined2 *)(puVar4 + 4) = 2;
    }
    else if (cVar1 == '\x02') {
      *(undefined1 *)((int)puVar4 + 0x12) = 3;
      puVar4[2] = puVar4[1] + 3 >> 2;
      *(undefined2 *)(puVar4 + 4) = 4;
    }
    else if (cVar1 == '\x04') {
      *(undefined1 *)((int)puVar4 + 0x12) = 4;
      puVar4[2] = puVar4[1] + 1 >> 1;
      *(undefined2 *)(puVar4 + 4) = 0x10;
    }
    else if (cVar1 == '\b') {
      *(undefined1 *)((int)puVar4 + 0x12) = 2;
      puVar4[2] = puVar4[1];
      *(undefined2 *)(puVar4 + 4) = 0x100;
    }
    else {
      if (cVar1 != ' ') {
        iVar3 = 3;
        goto LAB_005e08ce;
      }
      *(undefined1 *)((int)puVar4 + 0x12) = 7;
      puVar4[2] = puVar4[1] << 2;
      *(undefined2 *)(puVar4 + 4) = 0x100;
    }
    if (((puVar4[2] * *puVar4 != 0) && (param_2 == '\0')) &&
       (iVar3 = ft_glyphslot_alloc_bitmap(*(undefined4 *)(*param_1 + 0x54)), iVar3 == 0)) {
      *(undefined1 *)((int)param_1 + 0x11) = 1;
    }
  }
LAB_005e08ce:
  return CONCAT44(param_4,iVar3);
}

