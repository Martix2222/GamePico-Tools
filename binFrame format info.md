
# This is the documentation file for the .binFrame file format

 - Each file consists of a header and the frame data stored either in uncompressed binary format, or in a compressed format.

## Header structure

 - The header always starts with two bytes \[bytes 0-1\]  representing an int16 that specifies the version number of the format. The version then determines the further structure of the header:

> ### V1
>
> \[*All integer values are saved in a big-endian unsigned format, unless specified otherwise*\]
>
> - The version umber in bytes 0-1 is set to 1
>
> - The bytes 2-9 contain two int32 values. The first one represents the width of the image and the second one the height.
>
> - Bytes 10-13 contain an int32 value representing the sequential id of the frame. (frame 0 will have id 0, frame 1 will have id 1 and so on...)
>
> - Bytes 14-17 contain an int32 value that represents the time in ms of how long was the current frame displayed. This data is only written with the creation of the following frame, otherwise the bytes remain 0. If the bytes are 0 the file should be treated as a screenshot, instead as a part of a recording.
>  
> - Each bit in byte 18 represents a flag that determines the structure of the data. Currently these bits are implemented:
>
>   0. If bit 0 (counting from LSB = rightmost bit) is set to 1, the data following the header is compressed by the GZIP algorithm, otherwise the data is uncompressed. The compression algorithm window size is specified as an int8 on byte 19 of the header. It specifies directly the wbits argument of the function. During decompression the same or larger value has to be used. In normal python it is just fine to use the gzip builtin library, because by default it has the wbits set to the maximum value. If you want to use the zlib library instead, you have to adhere to its documentation and make sure that the wbits argument is set to the proper value for a gzip file. (usually 16 + (8 to 15)\[That's the window size on the byte 19\])
>
>>  - (Other flags might get implemented later on.)
>
> - Bytes 19 to 31 are reserved as padding and might be used later on to carry additional information if certain flags are set to 1.
>
> - The data starts on byte 32.

