/*
 * COPYRIGHT (c) 2010-2024 MACRONIX INTERNATIONAL CO., LTD
 * SPI Flash Low Level Driver (LLD) Sample Code
 *
 * FOR UNRESTRICTED INTERNAL USE ONLY
 * UNAUTHORIZED REPRODUCTION AND/OR DISTRIBUTION IS STRICTLY PROHIBITED.
 * ------------------------------------------------------------------------
 * This software code and all associated documentation, comments or other 
 * information (collectively "Software") is provided "AS IS" without
 * warranty of any kind. MACRONIX INTERNATIONAL Co., LTD ("MXIC") does  
 * not warrant the functions contained in the program will meet your
 * requirements or that the operation of the program will be uninterrupted
 * or error-free. IN NO EVENT, UNLESS REQUIRED BY APPLICABLE LAW OR AGREED
 * TO IN WRITING, MXIC OR ANY PERSON BE LIABLE FOR ANY LOSS, EXPENSE OR
 * DAMAGE, OF ANY TYPE OR NATURE ARISING OUT OF THE USE OF, OR INABILITY
 * TO USE THIS SOFTWARE OR PROGRAM, INCLUDING, BUT NOT LIMITED TO, CLAIMS,
 * SUITS OR CAUSES OF ACTION INVOLVING ALLEGED INFRINGEMENT OF COPYRIGHTS,
 * PATENTS, TRADEMARKS, TRADE SECRETS, OR UNFAIR COMPETITION.
 *
 * SPI and QPI interface command set
 *
 * $Id: SPI_BITBANG.c,v 1.1.1.1 2019/10/29 05:43:38 mxclldb1 Exp $
 */
#include "SPI_BITBANG.h"

/*
 * Function:       Initial_Spi
 * Arguments:      None
 * Description:    Initial spi flash state and wait flash warm-up
 *                 (enable read/write).
 * Return Message: None
 */
void Initial_Spi()
{
    //--- insert your chip select code here. ---//

    // Wait flash warm-up
}

/*
 * Function:       CS_Low, CS_High
 * Arguments:      None.
 * Description:    Chip select go low / high.
 * Return Message: None.
 */
void CS_Low()
{
    //--- insert your chip select code here. ---//
 
}

void CS_High()
{
    //--- insert your chip select code here. ---//

}
/*
 * Function:       HAL_Delay_Us
 * Arguments:      None
 * Description:    wait a delay time(us.) as specified
 *                 (enable read/write).
 * Return Message: None
 */
void HAL_Delay_Us(uint32 delay_us )
{
    //--- insert your code here. ---//


}

/*
 * Function:       InsertDummyCycle
 * Arguments:      dummy_cycle, number of dummy clock cycle
 * Description:    Insert dummy cycle of SCLK
 * Return Message: None.
 */
void InsertDummyCycle( uint8 dummy_cycle )
{
    //--- insert your code here. ---//

}
/*
 * Function:       SendByte
 * Arguments:      byte_value, data transfer to flash
 *                 transfer_type, select different type of I/O mode.
 *                 Seven mode:
 *                 SIO, single IO
 *                 DIO, dual IO
 *                 QIO, quad IO
 *                 PIO, parallel
 *                 DTSIO, double transfer rate SIO
 *                 DTDIO, double transfer rate DIO
 *                 DTQIO, double transfer rate QIO
 *                 STOIO, octa IO
 * Description:    Send one byte data to flash
 * Return Message: None.
 */
void SendByte( uint8 byte_value, uint8 transfer_type )
{
#ifdef MCU_Platform
    switch( transfer_type )
    {
#ifdef SIO
    case SIO: // Single I/O
        //--- insert your code here for single IO transfer. ---//
        break;
#endif
#ifdef DIO
    case DIO: // Dual I/O
        //--- insert your code here for dual IO transfer. ---//
        break;
#endif
#ifdef QIO
    case QIO: // Quad I/O
        //--- insert your code here for quad IO transfer. ---//
        break;
#endif
#ifdef STOIO
    case STOIO: //double transfer rate STOIO 
        //--- insert your code here for STOIO transfer. ---//
        break;
#endif
#ifdef PIO
    case PIO: // Parallel I/O
        //--- insert your code here for parallel IO transfer. ---//
        break;
#endif
#ifdef DTSIO
    case DTSIO: // Double transfer rate Single I/O
        //--- insert your code here for DT single IO transfer. ---//
        break;
#endif
#ifdef DTDIO
    case DTDIO: // Double transfer rate Dual I/O
        //--- insert your code here for DT dual IO transfer. ---//
        break;
#endif
#ifdef DTQIO
    case DTQIO: // Double transfer rate Quad I/O
        //--- insert your code here for DT quad IO transfer. ---//
        break;
#endif
    default:
        break;
    }
#endif  /* End of SendByte */
}
/*
 * Function:       GetByte
 * Arguments:      byte_value, data receive from flash
 *                 transfer_type, select different type of I/O mode.
 *                 Seven mode:
 *                 SIO, single IO
 *                 DIO, dual IO
 *                 QIO, quad IO
 *                 PIO, parallel IO
 *                 DTSIO, double transfer rate SIO
 *                 DTDIO, double transfer rate DIO
 *                 DTQIO, double transfer rate QIO
 *                 STOIO, octa IO
 * Description:    Get one byte data to flash
 * Return Message: 8 bit data
 */
uint8 GetByte( uint8 transfer_type )
{

#ifdef MCU_Platform
    switch( transfer_type )
    {
#ifdef SIO
    case SIO: // Single I/O
        //--- insert your code here for single IO receive. ---//
        break;
#endif
#ifdef DIO
    case DIO: // Dual I/O
        //--- insert your code here for dual IO receive. ---//
        break;
#endif
#ifdef QIO
    case QIO: // Quad I/O
        //--- insert your code here for qual IO receive. ---//
        break;
#endif
#ifdef STOIO
    case STOIO: //double transfer rate STOIO 
        //--- insert your code here for STOIO transfer. ---//
        break;
#endif
#ifdef PIO
    case PIO: // Parallel I/O
        //--- insert your code here for parallel IO receive. ---//
        break;
#endif
#ifdef DTSIO
    case DTSIO: // Double transfer rate Single I/O
        //--- insert your code here for DT single IO receive. ---//
        break;
#endif
#ifdef DTDIO
    case DTDIO: // Double transfer rate Dual I/O
        //--- insert your code here for DT dual IO receive. ---//
        break;
#endif
#ifdef DTQIO
    case DTQIO: // Double transfer rate Qual I/O
        //--- insert your code here for DT quad IO receive. ---//
#endif
    default:
        break;
    }
#endif  /* End of GetByte */
    return data_buf;
}
/*
 * Function:       SendHalfWord
 * Arguments:      half_word_value, data transfer to flash for DTOIO mode
 * Description:    Send half word data to flash
 * Return Message: None.
 */
void SendHalfWord( uint16 half_word_value )
{

	//---insert your chip select code here. ---//

}
/*
 * Function:       GetHalfWord
 * Arguments:      none
 * Description:    Get half word data from flash for DTOIO mode
 * Return Message: 16 bit data
 */
uint16 GetHalfWord( )
{
	//--- insert your chip select code here. ---//
}
