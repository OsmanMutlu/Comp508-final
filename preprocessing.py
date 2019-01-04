import numpy as np
import cv2
import argparse

def main():

    cv2.namedWindow("asd", cv2.WINDOW_NORMAL)

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

    # cv2.imshow("asd", contrasted)
    # cv2.waitKey(0)
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
    (H, W) = image.shape[:2]
    center = (W // 2, H // 2) # // returns an int
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(gray, M, (W, H),
                             flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # Apply threshold, now our image is binarized.
    binarized = cv2.threshold(rotated, 0, 255,
                           cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    cv2.imshow("asd", rotated)
    cv2.waitKey(0)    
    # LINE SEPERATION
    # binarized = rotated.copy()
    binarized[binarized > 0] = 1

    hist = np.sum(binarized, 1)
    # print(hist)

    # hist = cv2.threshold(np.array(hist, dtype=np.uint8), 0, 255,
    #                      cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1].reshape(-1)

    # hist = cv2.adaptiveThreshold(np.array(hist, dtype=np.uint8), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 0)
    
    # print(hist)
    # We need to get rid of this assumption somehow!!
    pixel_error = H // 75 # empirical
    lines = []
    isfirstline = True
    count = 0
    # counts = []
    for h in range(len(hist)):
        if isfirstline:
            if hist[h] > pixel_error:
                lines.append(max(h-1,0))
                isfirstline = False
        else:
            if hist[h] <= pixel_error:
                count += 1
            elif hist[h] > pixel_error and count != 0:
                # counts.append([h - (count // 2), count])
                lines.append(h - (count // 2))
                count = 0

    # for h in range(len(hist)):
    #     if isfirstline:
    #         if hist[h] != 0:
    #             lines.append(max(h-1,0))
    #             isfirstline = False
    #     else:
    #         if hist[h] == 0:
    #             count += 1
    #         elif hist[h] != 0 and count != 0:
    #             # counts.append([h - (count // 2), count])
    #             lines.append(h - (count // 2))
    #             count = 0

    lines.append(min(len(hist) - count + 1,W - 1)) # Adding last line
    # We can determine possible seperating points and then seperate lines where these possible points come together.
    # th_line = np.percentile(hist[hist != 0], 25)
    # print(th_line)
    # possible_lines = [y for y in range(2, len(hist) - 2) if hist[y]<=th_line and hist[y-2]>=hist[y-1] and hist[y-1]>=hist[y] and hist[y]<=hist[y+1] and hist[y+1]<=hist[y+2]]

    # possible_distances = [possible_lines[i] - possible_lines[i-1] for i in range(1,len(possible_lines) - 1)]
    # median_distance = np.percentile(possible_distances, 50)
    # pixel_error = h // 100 # Totally empirical

    # lines = []
    # # Adding first line
    # for h in range(len(hist)):
    #     if hist[h] != 0 and h != 0:
    #         lines.append(h)
    #         break
    #     elif hist[h] != 0 and h == 0:
    #         lines.append(0)
    #         break
            
    # for i in range(len(possible_lines)):
    #     if i == 0:
    #         if possible_lines[i+1] - possible_lines[i]>=median_distance - pixel_error:
    #             lines.append(possible_lines[i])

    #     elif i == len(possible_lines) - 1:
    #         if possible_lines[i] - possible_lines[i-1]>=median_distance - pixel_error:
    #             lines.append(possible_lines[i])

    #     else:
    #         if possible_lines[i] - possible_lines[i-1]>=median_distance - pixel_error and possible_lines[i+1] - possible_lines[i]>=median_distance - pixel_error:
    #             lines.append(possible_lines[i])

    # # Adding last line
    # for h in range(len(hist)-1,0,-1):
    #     if hist[h] != 0 and h != len(hist) - 1:
    #         lines.append(h)
    #         break
    #     elif hist[h] != 0 and h == len(hist) - 1:
    #         lines.append(len(hist) - 1)
    #         break


    asd = rotated.copy()
    for y in lines:
        asd = cv2.line(asd, (0,y), (W, y), (200,0,0), 1)

    cv2.imshow("asd", asd)
    cv2.waitKey(0)

    print(H,",", W)
    chars = []
    # WORD SEGMENTATION
    word_lines_per_line = []
    for y in range(1,len(lines)):

        word_lines = []
        hist = np.sum(binarized[lines[y-1]:lines[y],0:W], 0)

        hist = cv2.threshold(np.array(hist, dtype=np.uint8), 0, 255,
                                cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        isfirstword = True
        count = 0
        counts = []
        for h in range(len(hist)):
            if isfirstword:
                if hist[h] != 0:
                    word_lines.append(max(h-1,0)) # max because if it is the first pixel
                    isfirstword = False
            else:
                if hist[h] == 0:
                    count += 1
                elif hist[h] != 0 and count != 0:
                    counts.append([h - (count // 2), count])
                    count = 0

        distance = cv2.threshold(np.array([c[1] for c in counts], dtype=np.uint8), 0, 255,
                                cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        counts = np.array(counts)
        distance = distance.reshape(-1)
        word_lines.extend([c[0] for c in counts[distance > 0]])

        word_lines.append(min(len(hist) - count + 1,W - 1)) # Adding last line

        for l in range(len(word_lines)):
            asd = cv2.line(asd, (word_lines[l],lines[y]), (word_lines[l], lines[y-1]), (200,0,0), 1)

        word_lines_per_line.append(word_lines)

    # We don't to this part inside the original loop, because we need every word for taking average
    # Calculate average character width
    # Average word width divided by 5 which is average word length in english
    avg_char_len = int(np.mean([word_lines[i+1] - word_lines[i] for i in range(len(word_lines)-1) for word_lines in word_lines_per_line])) // 5

    print(avg_char_len)

    for y in range(1,len(lines)):

        word_lines = word_lines_per_line[y-1]
        for l in range(len(word_lines)-1):

            hist = np.sum(binarized[lines[y-1]:lines[y],word_lines[l]:word_lines[l+1]], 0)

            # print(hist)
            hist = cv2.threshold(np.array(hist, dtype=np.uint8), 0, 255,
                                 cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1].reshape(-1)

            # print(hist)
            possible_lines = []
            isfirstchar = True
            count = 0
            counts = []
            for h in range(len(hist)):
                if isfirstchar:
                    if hist[h] != 0:
                        possible_lines.append(max(h-1,0)) # max because if it is the first pixel
                        isfirstchar = False
                else:
                    if hist[h] == 0:
                        count += 1
                    elif hist[h] != 0 and count != 0:
                        # counts.append([h - (count // 2) - 1, count])
                        possible_lines.append(h - (count // 2))
                        count = 0

            # if counts:
            #     distance = cv2.threshold(np.array([c[1] for c in counts], dtype=np.uint8), 0, 255,
            #                              cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

            #     counts = np.array(counts)
            #     distance = distance.reshape(-1)
            #     char_lines.extend([c[0] for c in counts[distance > 0]])

            possible_lines.append(min(len(hist) - count + 1,word_lines[l+1])) # Adding last line

            # print(possible_lines)
            char_lines = []
            for i in range(avg_char_len,word_lines[l+1] - word_lines[l] - avg_char_len,avg_char_len):
                char_lines.append(possible_lines[np.argmin([abs(line - i) for line in possible_lines])])

            # print(char_lines)
            # print("-----------------------------")

            if char_lines:
                chars.append(rotated[lines[y-1]:lines[y],word_lines[l]:word_lines[l] + char_lines[0]])
                chars.extend([rotated[lines[y-1]:lines[y],word_lines[l] + char_lines[c]:word_lines[l] + char_lines[c+1]] for c in range(len(char_lines) - 1) if char_lines[c+1] != char_lines[c]])
                chars.append(rotated[lines[y-1]:lines[y],word_lines[l] + char_lines[-1]:word_lines[l+1]])
            else:
                chars.append(rotated[lines[y-1]:lines[y],word_lines[l]:word_lines[l+1]])

            # Baseline. Just uses average char width
            # if word_lines[l+1] - word_lines[l] > (avg_char_len + (avg_char_len // 2)):
            #     last_line = ((word_lines[l+1] - word_lines[l]) // avg_char_len) * avg_char_len
            #     chars.extend([rotated[lines[y-1]:lines[y],word_lines[l] + c:word_lines[l] + c + avg_char_len] for c in range(0,last_line,avg_char_len)])
            #     if word_lines[l+1] - word_lines[l] != last_line:
            #         chars.append(rotated[lines[y-1]:lines[y],word_lines[l] + last_line:word_lines[l+1]])
            # else:
            #     chars.append(rotated[lines[y-1]:lines[y],word_lines[l]:word_lines[l+1]])

            # if last_line:
            #     char_lines = [c for c in range(0,last_line,avg_char_len)]

            # for c in range(len(char_lines)):
            #     asd = cv2.line(asd, (word_lines[l] + char_lines[c],lines[y]), (word_lines[l] + char_lines[c], lines[y-1]), (60,0,0), 1)


    cv2.imshow("asd", asd)
    cv2.waitKey(0)

    for i in range(20):
        # print(chars[i])
        cv2.imshow("char", chars[i])
        cv2.waitKey(0)

if __name__ == '__main__':
    main()
