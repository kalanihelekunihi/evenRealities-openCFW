
undefined4 SVC_KvdbInvalidateMagic(void)

{
  SVC_FlashDBBlobWrite(0,DAT_004d9ae0,&stack0xfffffff8,4);
  return 0;
}

