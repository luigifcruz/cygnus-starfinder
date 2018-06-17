from itertools import combinations
from PIL import Image
from PIL.ExifTags import TAGS
import numpy as np
import math as m
import cv2

def decode(exif):
	return float(exif[0])/float(exif[1])

def get_exif(img):
	return {
		TAGS[k]: v
		for k, v in img._getexif().items()
		if k in TAGS
	}

def main():
	path = "./Lapse0/IMG_4096.JPEG"
	raw_img = Image.open(path)

	exif = get_exif(raw_img)

	w = exif['ExifImageWidth']
	h = exif['ExifImageHeight']
	fl = decode(exif['FocalLength'])/100
	yr = decode(exif['FocalPlaneYResolution'])
	xr = decode(exif['FocalPlaneXResolution'])

	ys = (h/yr)*0.254
	xs = (w/xr)*0.254

	hfov = 2*m.atan((xs)/(2*fl))
	vfov = 2*m.atan((ys)/(2*fl))

	px_hfov = hfov/w
	px_vfov = vfov/h

	print("========== Image Info ==========")
	print("Date/Time: %s" % exif['DateTimeDigitized'])
	print("Color Depth: %d" % raw_img.bits)
	print("Format: %s" % raw_img.format)
	print("========= Measurements =========")
	print("Width (px): %d" % w)
	print("Height (px): %d" % h)
	print("Focal Length (mm): %.1f" % (fl*100))
	print("Sensor Width (mm): %.1f" % (ys*100))
	print("Sensor Height (mm): %.1f" % (xs*100))
	print("Focal X Resolution (dpi): %.0f" % xr)
	print("Focal Y Resolution (dpi): %.0f" % yr)
	print("HFOV (deg): %.4f" % m.degrees(hfov))
	print("VFOV (deg): %.4f" % m.degrees(vfov))
	print("Horizontal Pixel (deg): %.6f" % m.degrees(px_hfov))
	print("Vertical Pixel (deg): %.6f" % m.degrees(px_vfov))
	print("============ Result ============")

	raw_img = cv2.cvtColor(np.array(raw_img)[:-1500], cv2.COLOR_BGR2GRAY)

	img = cv2.bitwise_not(raw_img)
	img = cv2.threshold(img, 80, 255, cv2.THRESH_BINARY)[1]
	img = cv2.bitwise_not(img)
	
	el = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
	img = cv2.dilate(img, el, iterations=6)

	cv2.imwrite("dilated.png", img)
	
	(_, contours, hierarchy) = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

	drawing = raw_img

	centers = []
	for i, contour in enumerate(contours):
		ms = cv2.moments(contour)
		center = (str(i), (int(ms['m10'] / ms['m00']), int(ms['m01'] / ms['m00'])))
		centers.append(center)
	
		cv2.circle(drawing, center[1], 30, (0, 0, 255), 2)
		font = cv2.FONT_HERSHEY_SIMPLEX
		cv2.putText(drawing, str(i), (center[1][0],center[1][1]-40), font, 1, (255,255,255), 2, cv2.LINE_AA)

	print("Suitable Stars Found: %d" % len(centers))
	cv2.imwrite("drawing.png", drawing)

	comb_stars = list(combinations(centers, 2))
	print("Possible Combinations: %d" % len(comb_stars))

	for stars in comb_stars:
		(s1_x, s1_y) = (stars[0][1][0], stars[0][1][1])
		(s2_x, s2_y) = (stars[1][1][0], stars[1][1][1])

		(d_x, d_y) = (abs(s1_x-s2_x)*px_hfov, abs(s1_y-s2_y)*px_vfov)
		hip = m.sqrt(pow(d_x, 2)+pow(d_y, 2))
		if stars[0][0] == '73' and stars[1][0] == '79':
			print(stars[0][0], stars[1][0], np.degrees(hip))

	print("================================")

main()
