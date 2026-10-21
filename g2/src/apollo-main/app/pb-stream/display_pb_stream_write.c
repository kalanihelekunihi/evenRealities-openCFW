/* Native nanopb stream writer 0x490616. */
#include <stdint.h>
struct pb_ostream_candidate {
    uint32_t (*callback)(void *,const uint8_t *,uint32_t);
    void *state; uint32_t max_size,bytes_written; const char *errmsg;
};
static const char pb_stream_full[]="stream full"; /* native 0x78b6a8 via 0x4910ac */
static const char pb_io_error[]="io error"; /* native 0x78b6b4 via 0x4910b0 */
uint32_t audio_pb_stream_write_490616(struct pb_ostream_candidate *stream,const void *buffer,uint32_t size)
{
    uint32_t sum;
    if (size!=0u && stream->callback!=0) {
        sum=size+stream->bytes_written;
        if (sum<stream->bytes_written || sum>stream->max_size) {
            if (stream->errmsg==0) stream->errmsg=pb_stream_full;
            return 0u;
        }
        if (!stream->callback(stream,(const uint8_t *)buffer,size)) {
            if (stream->errmsg==0) stream->errmsg=pb_io_error;
            return 0u;
        }
    }
    stream->bytes_written+=size;
    return 1u;
}
