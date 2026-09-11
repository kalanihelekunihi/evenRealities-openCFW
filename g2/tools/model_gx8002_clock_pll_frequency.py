# SPDX-License-Identifier: MIT
"""Integer PLL model; decoded equivalence remains unproved."""
MASK=0xffffffff

def quantize_input(frequency):
    if 16000<=frequency<48000:return 32000
    if 512000<=frequency<1536000:return 1024000
    if 153600<=frequency<3072000:return 2048000
    return None

def frequency(div_in_register,feedback_low,feedback_high,output_register,band_register):
    if any(not 0<=v<=MASK for v in (div_in_register,feedback_low,feedback_high,output_register,band_register)):
        raise ValueError('PLL words must be unsigned32')
    div_in=(div_in_register&63)+1
    div_fb=((feedback_low|((feedback_high&31)<<8))+1)&MASK
    div_out=((output_register&7)+1)*2
    if not div_fb:raise ValueError('Unqualified zero feedback divisor')
    oscillator=(61440000,73728000,86016000,98304000)[(band_register>>4)&3]
    selected=quantize_input(((oscillator*div_in)&MASK)//div_fb)
    if selected is None:return MASK
    return (((selected//div_in)*div_fb)&MASK)//div_out
