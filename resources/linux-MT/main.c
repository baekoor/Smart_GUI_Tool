/*
 * Copyright (c) 2021, Medallion Instrumentation Systems LLC
 * Mark Piotrowski <mpiotrowski@medallionis.com>
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

int main(int argc, char* argv[])
{
	int i;
	int cs;

	static const int headerSize = 6;
	char buf[1056];
	long lSize;

	char * in;
	char * out;

	ssize_t n;
	ssize_t nout;
	ssize_t bytes;

	/* ... */

	FILE *fp;

	if(argc != 3) {
		printf("usage: MF infilename outfilename\n");
		return -1;
	}

	in = argv[1];
	out = argv[2];

	snprintf(buf, headerSize + 1, "RZA2M:");

	fp = fopen(in, "rb");

	if(!fp) {
		printf("error: %s open failed\n", in);
		return -1;
	}

	// obtain file size:
	fseek (fp , 0 , SEEK_END);
	lSize = ftell (fp);
	rewind (fp);

	if(lSize > 1024) {
		printf("error: %s too large\n", in);
		return -1;
	}

	n = fread((void *)(buf + headerSize), 1, lSize, fp);

	if(n != lSize) {
		printf("error: %s read failed(%ld)\n", in, n);
		fclose(fp);
		return -1;
	}

	fclose(fp);

	/* ... */

	cs = 0;
	for(i = headerSize; i < (headerSize + n); i++) {
		cs ^= buf[i];
	}

	snprintf(buf + headerSize + n, headerSize, "*%02X", cs);

	fp = fopen(out, "w+");

	if(!fp) {
		printf("error: %s open failed\n", out);
		return -1;
	}

	nout = fwrite(buf, 1, headerSize + n + 3, fp);

	if(nout != (headerSize + n + 3)) {
		printf("error: %s write failed(%ld)\n", out, nout);
		fclose(fp);
		return -1;
	}

	fclose(fp);

	return(0);        
}

