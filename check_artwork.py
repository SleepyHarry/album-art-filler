import sys
from lxml import etree

if not __name__=="__main__":
    raise ImportWarning("Incorrect usage")
    sys.exit()

filepath = "C:\Users\Harry\Music\iTunes\iTunes Music Library.xml"

lib = etree.parse(open(filepath))

#I sure hope this structure stays the same
track_list = lib.getroot()[0].findall("dict")[0].findall("dict")

missing_art = []
for track in track_list:
    kids = track.getchildren()
    keytexts = [k.text for k in kids if k.tag == "key"]
    
    if not "Artwork Count" in keytexts and not "Podcast" in keytexts:
        missing_art.append(track)

if not missing_art:
    print "All artwork present"
    
    a = os.path.join(os.curdir, "resource/_missing.txt")
    b = os.path.join(os.curdir, "resource/_missing_albums.txt")
    with open(a, 'w') as f, open(b, 'w') as g:
        #no missing artwork, so clear the file
        f.write("")
        g.write("")

    sys.exit(0)
else:
    def fprint(s, f, endl='\n'):
        print s
        f.write(s)
        f.write(endl)
    
    f = open(os.path.join(os.curdir, "resource/_missing.txt"), 'w')
    g = open(os.path.join(os.curdir, "resource/_missing_albums.txt"), 'w')
    fprint("Missing artwork from:\n", f)

    def find_by_key(element, key):
        kids = element.iterchildren()

        #there's a better way, I'm sure, but this is cute
        try:
            while next(kids).text != key:
                pass
            else:
                return next(kids).text
        except StopIteration:
            #we couldn't find the key
            return "[No {}]".format(key)

    missing_albums = set()
    for track in missing_art:
        kids = track.iterchildren()

        artist = find_by_key(track, "Artist")
        song = find_by_key(track, "Name")
        album = find_by_key(track, "Album")

        fprint("{artist} - {song} ({album})".format(**locals()), f)

        missing_albums.add((artist,
                            album if not album == "[No Album]" else song))

    for artist, album in missing_albums:
        g.write("{artist} {album}\n".format(**locals()))

    f.close()
    g.close()
