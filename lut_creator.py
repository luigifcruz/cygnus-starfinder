from itertools import combinations
from hurry.filesize import size, si
import math as m
import numpy as np
import csv
import sys

max_mag = 3
max_angle = 180.0

def read_csv(path):
	with open(path) as f:
		reader = csv.DictReader(f)
		return [r for r in reader]

def main():
	stars = read_csv("./hygdata_v3.csv")

	fi_stars = [d for d in stars if float(d['mag']) < max_mag]
	comb_stars = list(combinations(fi_stars, 2))

	print("======== STAR LUT CREATOR ========")
	print("N of Stars: %d" % len(stars))
	print("N of Filtered Stars: %d" % len(fi_stars))
	print("N of Binary Combinations: %d" % len(comb_stars))
	print("============ RESULTS =============")

	lut = []
	for stars in comb_stars:
		(s1_x, s1_y, s1_z) = (float(stars[0]['x']), float(stars[0]['y']), float(stars[0]['z']))
		(s2_x, s2_y, s2_z) = (float(stars[1]['x']), float(stars[1]['y']), float(stars[1]['z']))

		dot_prod = (s1_x*s2_x)+(s1_y*s2_y)+(s1_z*s2_z)
		sum_prod = m.sqrt(pow(s1_x, 2)+pow(s1_y, 2)+pow(s1_z, 2))*m.sqrt(pow(s2_x, 2)+pow(s2_y, 2)+pow(s2_z, 2))
		theta = m.acos(dot_prod/abs(sum_prod))

		if theta < m.radians(max_angle):
			interaction = (int(stars[0]['id']), int(stars[1]['id']), m.degrees(theta))
			lut.append(interaction)

	print("N of Valid Combinations: %d" % len(lut))
	print("LUT Memory Size: %s" % size(sys.getsizeof(lut), system=si))
	print("==================================")

	b = open('./stars_lut.csv', 'w')
	a = csv.writer(b)
	a.writerows(lut)
	b.close()

	np.save("./stars_lut", lut)

main()
