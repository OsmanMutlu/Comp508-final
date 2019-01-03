import numpy as np
import cv2
import argparse

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", required=True, help="input image file")
    args = parser.parse_args()

    image = cv2.imread(args.image)

    # Make image grayscale and make background black and writing white. (White text is better in my opinion.)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)

    # Apply threshold, now our image is binarized.
    contrasted = cv2.threshold(gray, 0, 255,
                           cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # DE-SKEWING
    # We find the minimum rectangle that contains all the pixels that are greater than zero
    coords = np.column_stack(np.where(contrasted > 0))
    angle = cv2.minAreaRect(coords)[-1]

    # minAreaRect return angles between -90 to 0.
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Rotation. Need to look into this more !!!!!!!!!
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2) # // returns an int
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(contrasted, M, (w, h),
                             flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # LINE SEPERATION
    hist = cv2.reduce(rotated,1, cv2.REDUCE_AVG).reshape(-1)

    # We can determine possible seperating points and then seperate lines where these possible points come together.
    th_line = 2
    uppers = [y for y in range(h-1) if hist[y]<=th_line and hist[y+1]>th_line]
    lowers = [y for y in range(h-1) if hist[y]>th_line and hist[y+1]<=th_line]

    asd = rotated.copy()
    for y in lowers:
        asd = cv2.line(asd, (0,y), (w, y), (200,0,0), 1)

    print(h,",", w)
    th_word = 1
    th_char = 4
    chars = []
    # WORD SEGMENTATION
    for y in range(len(lowers)):
        if y == 0:
            hist = cv2.reduce(rotated[0:lowers[y],0:w],0, cv2.REDUCE_AVG).reshape(-1)

            lefts = [x for x in range(w-1) if hist[x]<=th_word and hist[x+1]>th_word]

            # print(lefts)
            for l in range(len(lefts)):
                asd = cv2.line(asd, (lefts[l],0), (lefts[l], lowers[y]), (200,0,0), 1)

            for l in range(len(lefts)):
                if l == len(lefts) - 1:
                    char_lefts = [x for x in range(len(hist[lefts[l]:]) - 1) if hist[x+lefts[l]]<=th_char and hist[x+1+lefts[l]]>th_char]
                    chars.extend([rotated[0:lowers[y],lefts[l] + char_lefts[c]:lefts[l] + char_lefts[c+1]] for c in range(len(char_lefts) - 1)])
                    chars.append(rotated[0:lowers[y],lefts[l] + char_lefts[-1]:])
                else:
                    char_lefts = [x for x in range(len(hist[lefts[l]:lefts[l+1]]) - 1) if hist[x+lefts[l]]<=th_char and hist[x+1+lefts[l]]>th_char]
                    chars.extend([rotated[0:lowers[y],lefts[l] + char_lefts[c]:lefts[l] + char_lefts[c+1]] for c in range(len(char_lefts) - 1)])
                    chars.append(rotated[0:lowers[y],lefts[l] + char_lefts[-1]:lefts[l+1]])

                print(char_lefts)
                for c in range(len(char_lefts)):
                    asd = cv2.line(asd, (lefts[l] + char_lefts[c],lowers[y]), (lefts[l] + char_lefts[c], lowers[y-1]), (60,0,0), 1)

        else:
            hist = cv2.reduce(rotated[lowers[y-1]:lowers[y],0:w], 0, cv2.REDUCE_AVG).reshape(-1)

            lefts = [x for x in range(w-1) if hist[x]<=th_word and hist[x+1]>th_word]

            # print(lefts)
            for l in range(len(lefts)):
                asd = cv2.line(asd, (lefts[l],lowers[y]), (lefts[l], lowers[y-1]), (200,0,0), 1)

            for l in range(len(lefts)):
                if l == len(lefts) - 1:
                    char_lefts = [x for x in range(len(hist[lefts[l]:]) - 1) if hist[x+lefts[l]]<=th_char and hist[x+1+lefts[l]]>th_char]                        
                    chars.extend([rotated[lowers[y-1]:lowers[y],lefts[l] + char_lefts[c]:lefts[l] + char_lefts[c+1]] for c in range(len(char_lefts) - 1)])
                    chars.append(rotated[lowers[y-1]:lowers[y],lefts[l] + char_lefts[-1]:])
                else:
                    char_lefts = [x for x in range(len(hist[lefts[l]:lefts[l+1]]) - 1) if hist[x+lefts[l]]<=th_char and hist[x+1+lefts[l]]>th_char]
                    chars.extend([rotated[lowers[y-1]:lowers[y],lefts[l] + char_lefts[c]:lefts[l] + char_lefts[c+1]] for c in range(len(char_lefts) - 1)])
                    chars.append(rotated[lowers[y-1]:lowers[y],lefts[l] + char_lefts[-1]:lefts[l+1]])

                print(char_lefts)
                for c in range(len(char_lefts)):
                    asd = cv2.line(asd, (lefts[l] + char_lefts[c],lowers[y]), (lefts[l] + char_lefts[c], lowers[y-1]), (60,0,0), 1)



    cv2.imshow("asd", asd)
    cv2.waitKey(0)

    # for char in chars:
    #     cv2.imshow("char", char)
    #     cv2.waitKey(0)

if __name__ == '__main__':
    main()
