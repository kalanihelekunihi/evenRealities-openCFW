
undefined4 * text_stream_create(void)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  int iVar3;
  
  puVar1 = (undefined4 *)file_heap_allocate(0x30);
  if (puVar1 == (undefined4 *)0x0) {
    puVar1 = (undefined4 *)0x0;
  }
  else {
    *puVar1 = 0;
    puVar1[1] = 0;
    puVar1[2] = 100;
    puVar1[3] = 0;
    puVar1[4] = 0;
    *(undefined1 *)(puVar1 + 5) = 0;
    puVar1[6] = 0;
    puVar1[7] = 0;
    puVar1[9] = 0;
    puVar1[10] = 0;
    *(undefined1 *)(puVar1 + 0xb) = 0;
    uVar2 = osMutexNew(0);
    puVar1[8] = uVar2;
    if (puVar1[8] == 0) {
      file_heap_free(puVar1);
      puVar1 = (undefined4 *)0x0;
    }
    else {
      iVar3 = ensure_text_capacity(puVar1,puVar1,puVar1 + 9,0x200);
      if (iVar3 == 0) {
        osMutexDelete(puVar1[8]);
        file_heap_free(puVar1);
        puVar1 = (undefined4 *)0x0;
      }
      else {
        iVar3 = ensure_text_capacity(puVar1,puVar1 + 1,puVar1 + 10,0x200);
        if (iVar3 == 0) {
          osMutexDelete(puVar1[8]);
          file_heap_free(*puVar1);
          file_heap_free(puVar1);
          puVar1 = (undefined4 *)0x0;
        }
        else {
          *(undefined1 *)*puVar1 = 0;
          *(undefined1 *)puVar1[1] = 0;
        }
      }
    }
  }
  return puVar1;
}

