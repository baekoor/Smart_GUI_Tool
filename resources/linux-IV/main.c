/*
 * Copyright (c) 2021, Medallion Instrumentation Systems LLC
 * Noel Lemouel <noel@medallionis.com>
 */

#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <libgen.h>
#include <stdint.h>
#include <sys/types.h>
#include <sys/stat.h>

#ifdef USE_LIBSSL
#include <openssl/md5.h>
#else
#include "md5.c"	// https://opensource.apple.com/source/cvs/cvs-19/cvs/lib/md5.c
#endif

#if defined _WIN32

#define WIN32_NO_STATUS
#include <windows.h>
#undef WIN32_NO_STATUS

#include <winternl.h>
#include <ntstatus.h>
#include <winerror.h>
// #include <stdio.h>
#include <bcrypt.h>
#include <sal.h>

void 
ReportError( 
	_In_	DWORD       dwErrCode 
    )
{
    wprintf( L"Error: 0x%08x (%d)\r", dwErrCode, dwErrCode );
}

int __WIN32_rng(BYTE *Buffer, DWORD BufferSize)
{
	NTSTATUS Status;

	memset(Buffer, 0, BufferSize);

	//
	// Fill the buffer with random bytes
	//

	Status = BCryptGenRandom (
			NULL,                       // Alg Handle pointer; NUll is passed as BCRYPT_USE_SYSTEM_PREFERRED_RNG flag is used
			Buffer,                     // Address of the buffer that recieves the random number(s)
			BufferSize,                 // Size of the buffer in bytes
			BCRYPT_USE_SYSTEM_PREFERRED_RNG); // Flags                  

	if( !NT_SUCCESS(Status) )
	{
		ReportError(Status);
		goto cleanup;
	}
/*
	int i;

	for(i=0; i<BufferSize; i++) {
		printf("0x%02x\n", Buffer[i]);
	}
*/
	Status = STATUS_SUCCESS;

cleanup:

	return (DWORD)Status;
}

#else

const unsigned char* urandom = "/dev/urandom";

#endif

int main(void)
{
	int i;

	unsigned char buf[512];

	ssize_t n;
	ssize_t bytes;

	/* ... */

#if defined _WIN32

	__WIN32_rng(buf, sizeof(buf));

#else

	FILE *fp;

	struct stat sb;

	if (stat(urandom, &sb) == -1) {
		printf("stat\n");
		return -1;
	}

	fp = fopen(urandom, "rb");

	if(!fp) {
		printf("error: %s open failed\n", urandom);
		return -1;
	}

	n = fread(buf, sizeof(buf), 1, fp);

	if(n != 1) {
		printf("error: %s read failed\n", urandom);
		fclose(fp);
		return -1;
	}

	fclose(fp);

#endif

	/* ... */
#ifdef USE_LIBSSL
/*
	MD5_Init(&c);
	bytes=read(STDIN_FILENO, buf, 512);
	while(bytes > 0)
	{
		MD5_Update(&c, buf, bytes);
		bytes=read(STDIN_FILENO, buf, 512);
	}
*/

	MD5_CTX c;

	unsigned char out[MD5_DIGEST_LENGTH];

	MD5_Init(&c);

	MD5_Update(&c, buf, sizeof(buf));

	MD5_Final(out, &c);

	for(n=0; n<MD5_DIGEST_LENGTH; n++)
		printf("%02x", out[n]);

	putchar((int)'\n');

	/* ... */
#else

	struct MD5Context context;

	uint8_t checksum[16];

	MD5Init (&context);
	MD5Update (&context, (void *)buf, sizeof(buf));
	MD5Final (checksum, &context);

	for (i = 0; i < 16; i++) {
		printf ("%02x", (unsigned int)checksum[i]);
	}

#if defined _WIN32
	printf ("\r");
#else
	printf ("\n");
#endif

#endif

	/* ... */

	return(0);        
}

