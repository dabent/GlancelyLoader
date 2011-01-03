import Image
import colorsys

def calculateColorFromHSV(hsv):
    HUE_BASE = 0.0
    HUE_RED_LOW_BASE = 0.0
    HUE_RED_LOW_MAX = 0.038
    HUE_ORANGE_BASE = 0.038
    HUE_ORANGE_MAX = 0.110
    HUE_YELLOW_BASE = 0.110 # was 0.120
    HUE_YELLOW_MAX = 0.160 # was 0.170
    HUE_GREEN_BASE = 0.160
    HUE_GREEN_MAX = 0.400
    HUE_BLUE_BASE = 0.400 # was 0.422
    HUE_BLUE_MAX = 0.700  # was 0.722
    HUE_PURPLE_BASE = 0.700
    HUE_PURPLE_MAX = 0.916
    HUE_RED_BASE = 0.916
    HUE_RED_MAX = 1.0
    HUE_MAX = 1.0

    UNKNOWN = 0
    RED = 1
    ORANGE = 2
    YELLOW = 3
    GREEN = 4
    BLUE = 5
    PURPLE = 6
    BLACK = 7
    WHITE = 8

    hue = hsv[0]
    saturation = hsv[1]
    brightness = hsv[2]

    color = 0
    
    if ((hue < 0.2) and (saturation < 0.2) and (brightness > 0.46)):
        #print "It's probably WHITE"
        color = WHITE
    elif ((saturation < 0.2) and (brightness <= 0.46)):
        #print "It's probably BLACK"
        color = BLACK
    elif ((hue >= HUE_RED_LOW_BASE) and (hue <= HUE_RED_LOW_MAX)):
        #print "It's probably ORANGE"
        color = RED
    elif ((hue >= HUE_ORANGE_BASE) and (hue <= HUE_ORANGE_MAX)):
        #print "It's probably ORANGE"
        color = ORANGE
    elif ((hue > HUE_YELLOW_BASE) and (hue <= HUE_YELLOW_MAX)):
        #print "It's probably YELLOW"
        color = YELLOW
    elif ((hue > HUE_GREEN_BASE) and (hue <= HUE_GREEN_MAX)):
        #print "It's probably GREEN"
        color = GREEN
    elif ((hue > HUE_BLUE_BASE) and (hue <= HUE_BLUE_MAX)):
        #print "It's probably BLUE"
        color = BLUE
    elif ((hue > HUE_PURPLE_BASE) and (hue <= HUE_PURPLE_MAX)):
        #print "It's probably PURPLE"
        color = PURPLE
    elif ((hue > HUE_RED_BASE) and (hue <= HUE_RED_MAX)):
        #print "It's probably RED"
        color = RED

    return color

    
def calculateImageColor(fileName):
    
    MAX_X = 75
    MAX_Y = 75
    X_OFFSET = 10
    X_OFFSET2 = 20
    Y_OFFSET = 10
    Y_OFFSET2 = 20
    
    rgbList = []
    im = Image.open(fileName)
    #print im.format, im.size, im.mode

    count = 0
    for x in range(X_OFFSET,MAX_X - X_OFFSET):
        for y in range(Y_OFFSET,MAX_Y - Y_OFFSET):
            rgbVal =  im.getpixel((x,y))
            if (((x < X_OFFSET2) or (x >= (MAX_X - X_OFFSET2))) or ((y < Y_OFFSET2) or (y >= (MAX_Y - Y_OFFSET2)))):
                rgbList.append(rgbVal)
            else:
 #               count = count + 1
                rgbList.append(rgbVal)
                rgbList.append(rgbVal)

#    print "Count: " + str(count)
    red = 0
    blue = 0
    green = 0
    for rgb in rgbList:
        red = red + rgb[0]
        green = green + rgb[1]
        blue = blue + rgb[2]

    red = red/len(rgbList)
    green = green/len(rgbList)
    blue = blue/len(rgbList)

    #print "Red: " + str(red) + " Green: " + str(green) + " Blue: " + str(blue)

    return calculateColorFromHSV(colorsys.rgb_to_hsv((red/256.0),(green/256.0),(blue/256.0)))

if __name__ == "__main__":

    color = calculateImageColor("/tmp/images/product/220217_75x75.jpg")

    print "The color is: " + str(color)
