
/* Full FT_Set_Transform525444..5254c8 132bytes.
 * Matrix/vector pointers retain native aliasing and read order. */
void audio_uart_ft_set_transform_525444(void *face,const int32_t *matrix,const int32_t *vector)
{
 if(face==0)return;
 void *internal=draw360_pointer(face,128u);
 draw360_store(internal,24u,0u);
 if(matrix==0){
  draw360_store(internal,0u,65536u);draw360_store(internal,4u,0u);
  draw360_store(internal,8u,0u);draw360_store(internal,12u,65536u);
  matrix=internal;
 }else audio_uart_checksum_copy(internal,matrix,16u);
 uint32_t xy=draw360_word(matrix,4u),yx=draw360_word(matrix,8u);
 if((xy|yx)!=0u || draw360_word(matrix,0u)!=65536u || draw360_word(matrix,12u)!=65536u)
  draw360_store(internal,24u,draw360_word(internal,24u)|1u);
 if(vector==0){draw360_store(internal,16u,0u);draw360_store(internal,20u,0u);vector=(const void *)((const uint8_t *)internal+16u);}
 else {uint32_t x=draw360_word(vector,0u),y=draw360_word(vector,4u);draw360_store(internal,16u,x);draw360_store(internal,20u,y);}
 uint32_t x=draw360_word(vector,0u),y=draw360_word(vector,4u);
 if((x|y)!=0u)draw360_store(internal,24u,draw360_word(internal,24u)|2u);
}
