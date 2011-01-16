import urllib
import json
import unicodedata
import datetime
import sys
import subprocess
import os
import shutil
import random

class EtsyClient:

    def __init__(self):
        self.DEFAULT_API_KEY = "9d9vs7xsey3yh2f4n8nxwn9v"
        self.baseURI = "http://openapi.etsy.com/v2/"
        self.apiEnvironment = "public/"

    def process(self, call, options):
        url = self.baseURI + self.apiEnvironment
        url = url + call
        options['api_key'] = self.DEFAULT_API_KEY
        params = urllib.urlencode(options)
        #print(url+"?%s" % params)
        f = urllib.urlopen(url+"?%s" % params)
        return f.read()

    
class ListingClient(EtsyClient):        

    def __init__(self):
        EtsyClient.__init__(self)

    def getActive(self, offset, limit):
        return EtsyClient.process(self, "listings/active", {'includes': 'Images:1,Shop', 'offset': offset, 'limit': limit})

def createLine(index, listing):
    line = None;
    try:
        images = listing['Images']
        if (images != None) and (len(images) > 0):
            image = images[0]
            allTags = ""
            allMaterials = ""
            title = listing['title']
            title = title.encode('ascii','ignore')
            title = title.strip()
            title = title.replace("'"," ")
            if len(title) > 255:
                title = title[0:250]
            line = "(" + str(index) + "," + str(listing['listing_id']) + ",'" + listing['state'] + "'," + str(listing['user_id']) + ",'" + title
            description = listing['description']
            description = description.encode('ascii','ignore')
            description = description.strip()
            description = description.replace("'"," ")
            line = line + "','" + "description" + "'," + str(listing['creation_tsz']) + "," + str(listing['ending_tsz'])
            line = line + "," + str(listing['original_creation_tsz']) + "," + str(listing['last_modified_tsz'])
            line = line + "," + str(listing['price']) + ",'" + listing['currency_code'] + "'," + str(listing['quantity'])

            if listing['tags'] == None:
                line = line +  ",'" + " "
            else:
                line = line +  ",'"
                for tag in listing['tags']:
                    tag = tag.replace("_", " ")
                    tag = tag.replace("'", " ")
                    allTags = allTags + " " + tag
                line = line + allTags

            if listing['materials'] == None:
                line = line +  "','" + " " 
            else:
                line = line +  "','"
                for material in listing['materials']:
                    material = material.replace("_", " ")
                    material = material.replace("'", " ")
                    allMaterials = allMaterials + " " + material
                line = line +  allMaterials

            if listing['shop_section_id'] == None:
                line = line +  "'," + "0"
            else:
                line = line +  "'," + str(listing['shop_section_id'])
                
            if listing['featured_rank'] == None:
                line = line +  "," + "0"
            else:
                line = line +  "," + str(listing['featured_rank'])
            line = line +  "," + str(listing['state_tsz'])

            # HSV
            hue = 0
            saturation = 0
            brightness = 0
            if listing['hue'] == None:
                line = line +  "," + "0"
            else:
                line = line +  "," + str(listing['hue'])
                hue = listing['hue']
            if listing['saturation'] == None:
                line = line +  "," + "0"
            else:
                line = line +  "," + str(listing['saturation'])
                saturation = listing['saturation']
            if listing['brightness'] == None:
                line = line +  "," + "0"
            else:
                line = line +  "," + str(listing['brightness'])
                brightness = listing['brightness']
                
            if listing['is_black_and_white']:
                line = line +  ",1"
            else:
                line = line +  ",0"

            line = line +  ",'" + listing['url']
            line = line +  "'," + str(listing['views'])
            line = line +  ",'" + image['url_75x75']
            line = line +  "','" + image['url_170x135']
            line = line +  "','" + image['url_570xN']
            line = line +  "','" + image['url_fullxfull']
            line = line +  "','" + allTags + allMaterials + title
            line = line +  "'," + "NOW()"
            line = line +  ",0"
            shop = listing['Shop']
            if shop != None:
                shopName = shop['shop_name']
                if shopName != None:
                    line = line +  ",'Etsy','" + shopName + "'," + str(random.getrandbits(64))
            else:
                line = line +  ",'','Etsy',"  + str(random.getrandbits(64))
            line = line +  "),\n"
    except:
        print "WTF"
        return None
    return line

def main(args):
    table = "listing"
    if len(args) > 0:
        print "I've got " + str(len(args)) + " args!"
        table = "listing2"
    else:
        print "No Args"
        
    print "Starting:"
    print datetime.datetime.now()

    lc = ListingClient()

    fout = open('/tmp/workfile.sql', 'w')
    fout.write("USE etsy_instant;\n")
    fout.write("truncate table " + table + ";\n")
    fout.write("/*!40000 ALTER TABLE `" + table + "` DISABLE KEYS */;\n" )

    # For 500 down to 0?

    offset = 500
    limit = 100

    #offsets = range(500,-1,-1)

    index = 1
    noException = True
    wroteLine = False

    for offset in range(500,-1,-1):
        try:
            print str(offset)
            result = lc.getActive(offset*limit,limit)
            if result == None:
                print("It's None")
            else:
                #print json.dumps(result, sort_keys=True, indent=4)
                lineCount = 0
                listingCount = 0
                listings = json.loads(result)
                insertLine = "";
                results = listings['results']
                for listing in results:
                    if lineCount == 0:
                        insertLine = "INSERT INTO `" + table + "` (`id`,`listing_id`,`state`,`user_id`,`title`,`description`,`creation_tsz`,`ending_tsz`,`original_creation_tsz`,`last_modified_tsz`,`price`,`currency_code`,`quantity`,`tags`,`materials`,`shop_section_id`,`featured_rank`,`state_tsz`,`hue`,`saturation`,`brightness`,`is_black_and_white`,`url`,`views`,`url_75x75`,`url_170x135`,`url_570xN`,`url_fullxfull`,`keyset`,`created`,`color`,`merchant`,`shop`,`sorter`) VALUES \n"
                    line = createLine(index, listing)
                    if line != None:
                        insertLine = insertLine + line
                        index = index + 1
                        if (lineCount == 25) or (len(results) == listingCount):
                            lineCount = 0
                            insertLine = insertLine[::-1]
                            insertLine = insertLine.replace(",",";",1)
                            insertLine = insertLine[::-1]
                            #print insertLine
                            fout.write(insertLine)
                        else:
                            lineCount = lineCount + 1                    
                    listingCount = listingCount + 1
        except ValueError as ex:
            print("value exception occurred ", ex)
            lineCount = 0
            noException = False
        except KeyError:
            print "KeyError\n"
            lineCount = 0
            noException = False

    fout.write("/*!40000 ALTER TABLE `" + table + "` ENABLE KEYS */;\n")
    fout.close()
    print "Ending:"
    print datetime.datetime.now()

if __name__ == "__main__":
    failure = False
    
    main(sys.argv[1:])

    tableArg = ""
    if len(sys.argv[1:]) > 0:
        tableArg = "listing2"

    #dump it into DB
    process = subprocess.Popen(["mysql -uinstantetsy -pmaverick -Detsy_instant < /tmp/workfile.sql"], shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE) #, stdout=subprocess.PIPE)
    output = process.stderr.read()
    if (len(output) > 0):
        print "Failed on import: " + output
        failure = True

    if (failure == False):
        if sys.platform == "win32":
            process = subprocess.Popen(["java -cp C:\home\dabent\loaders\EtsyAPIWrapper2.jar;C:\home\dabent\loaders\lib\commons-lang-2.4.jar;C:\home\dabent\loaders\lib\mysql-connector-java-5.1.11-bin.jar com.bentti.api.etsy.image.ColorManager " + tableArg], shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE) #, stdout=subprocess.PIPE)
        else:
            process = subprocess.Popen(["java -cp /home/dabent/loaders/EtsyAPIWrapper2.jar:/home/dabent/loaders/lib/commons-lang-2.4.jar:/home/dabent/loaders/lib/mysql-connector-java-5.1.11-bin.jar com.bentti.api.etsy.image.ColorManager " + tableArg], shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE) #, stdout=subprocess.PIPE)
        
        output = process.stderr.read()
#        if (len(output) > 0):
        print "Java Output: " + output
#            failure = True

        dst = "/var/www/listing.php"
        src1 = "/var/www/listing1.php"
        src2 = "/var/www/listing2.php"

        if tableArg == "":
            shutil.copyfile(src1, dst)
        else:
            shutil.copyfile(src2, dst)
    
        if sys.platform == "win32":
            process = subprocess.Popen(["/PROGRA~2/Git/bin/sh.exe", "-c", "/bin/cp /c/tmp/images/product/*.jpg /c/var/www/images/product"], shell=False, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        else:
            process = subprocess.Popen(["/bin/cp /tmp/images/product/*.jpg /var/www/images/product/"], shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            output = process.stderr.read()
            if (len(output) > 0):
                print "Images Move FAIL: " + output
                failure = True
            stdout_value = process.communicate()[0]
            print "Move images Results:"
            print stdout_value

   
        if sys.platform == "win32":
            process = subprocess.Popen(["/PROGRA~2/Git/bin/sh.exe", "-c", "/home/dabent/loaders/processCJSQL.bsh"], shell=False, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        else:
            process = subprocess.Popen(["/home/dabent/loaders/processCJSQL.bsh"], shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            output = process.stderr.read()
            if (len(output) > 0):
                print "Failed on CJ SQL: " + output
                failure = True
            stdout_value = process.communicate()[0]
            print "CJ SQL Results:"
            print stdout_value
