/* Analysis only: volatile register provider; NEVER executed on a device here. */
unsigned option_unlock_08004b6c(void) {
 unsigned status=1;
 if(read_cr() & (1u<<30)) {
  write_optkeyr(0x08192a3b);write_optkeyr(0x4c5d6e7f);
  if(!(read_cr() & (1u<<30)))status=0;
 }
 return status;
}
unsigned flash_unlock_08004bf4(void) {
 unsigned status=0;
 if(read_cr() & (1u<<31)) {
  write_keyr(0x45670123);write_keyr(0xcdef89ab);
  if(read_cr() & (1u<<31))status=1;
 }
 return status;
}
