
void semantic_CodecFreeFirmwareBuffers(void)

{
  int *piVar1;
  
  piVar1 = DAT_00578c58;
  if (*DAT_00578c58 != 0) {
    file_heap_free(*DAT_00578c58);
    *piVar1 = 0;
    *DAT_00578c54 = 0;
  }
  piVar1 = DAT_00578c78;
  if (*DAT_00578c78 != 0) {
    file_heap_free(*DAT_00578c78);
    *piVar1 = 0;
    *DAT_00578c74 = 0;
  }
  return;
}

