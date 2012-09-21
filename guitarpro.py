import struct
import sys
from locale import getpreferredencoding

def _hexdump(s):
    if isinstance(s, unicode):
        s = s.encode('utf-8')

    return ' '.join(['%02x' % ord(x) for x in s])

class NotGPFile(Exception):
    pass

class GuitarProFileSimple(object):
    _encoding = getpreferredencoding()

    def read_long_string(self, fo):
        s = fo.read(4)
        size = struct.unpack('l', s)[0]
        s = fo.read(1)
        if size == 0:
            size = ord(s)

        string = fo.read(size - 1)

        return string.decode(self._encoding)

    def read_byte_string(self, fo):
        s = fo.read(1)
#        print _hexdump(s)
        size_block = ord(s)
        s = fo.read(1)
#        print _hexdump(s)
        size_string = ord(s)

#        print size_string, size_block

        string = fo.read(size_string)

        fo.read(size_block - size_string - 1)

        return string.decode(self._encoding)

    def read_short_string(self, fo):
        s = fo.read(2)
#        print _hexdump(s)
        s = s[1] + s[0]
        size_block = struct.unpack('h', s)[0]
        s = fo.read(1)
#        print _hexdump(s)
        size_string = ord(s)

#        print size_string, size_block

        string = fo.read(size_string)

        fo.read(size_block - size_string - 2)

        return string.decode(self._encoding)

    def __init__(self, fo):
        fo.seek(0)

        head = fo.read(20)

        header_len = 0
        if head[1:19] == "FICHIER GUITAR PRO":
            header_len = 19
            fo.read(1)

        if head[1:20] == "FICHIER GUITARE PRO":
            header_len = 20
            fo.read(2)

        if header_len:
            self.version = fo.read(4)
            hsize = ord(head[0])
            fo.seek(hsize + 5 + 1)

            if self.version in ['1T\x03\x04']:
                fo.read(3)
                title = self.read_byte_string(fo)
                subtitle = ''
                artist = self.read_byte_string(fo)
            elif self.version in ['1.04', '1.02', '1.03']:
                title = self.read_byte_string(fo)
                subtitle = ''
                artist = self.read_byte_string(fo)
            elif self.version in ['2.21']:
                fo.read(1)
                title = self.read_byte_string(fo)
                subtitle = ''
                artist = self.read_byte_string(fo)
            else:
                fo.read(1)
                title = self.read_long_string(fo)
                subtitle = self.read_long_string(fo)
                artist = self.read_long_string(fo)

            if title:
                if subtitle:
                    self.title = '%s (%s)' % (title, subtitle)
                else:
                    self.title = title
            else:
                if subtitle:
                    self.title = title
                else:
                    self.title = ''

            self.artist = artist or ''

            return

        raise NotGPFile(u'Not a GP file')

if __name__ == '__main__':
    import os
    import codecs
    import sys

    sys.stdout = codecs.getwriter(getpreferredencoding())(sys.__stdout__)
    sys.stderr = codecs.getwriter(getpreferredencoding())(sys.__stderr__)

    def process_file(fullpath):
        if not os.path.getsize(fullpath):
            return

        f = open(fullpath, 'rb')
        try:
            gp = GuitarProFileSimple(f)
            print '\t'.join([fullpath, gp.version, gp.artist, gp.title])
        except NotGPFile:
            print >>sys.stderr, 'Wrong file', fullpath
        except:
            print >>sys.stderr, '[%s]' % fullpath
            raise
        finally:
            f.close()

    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        process_file(sys.argv[1])
    else:
        for path, dirs, files in os.walk(u'.'):
            for file in files:
                ext = file.rsplit('.', 1)[-1].lower()
                if ext in ['gtp', 'gp3', 'gp4', 'gp5']:
                    fullpath = os.path.join(path, file)
                    process_file(fullpath)
