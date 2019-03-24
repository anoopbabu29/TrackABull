


def is_same_direction(x1, y1, x2, y2):
	x = False
	y = False
	if ((x1 < 0 and x2 < 0) or (x1 > 0 and x2 > 0) or (x1 == x2)):
		x = True
	if ((y1 < 0 and y2 < 0) or (y1 > 0 and y2 > 0) or (y1 == y2)):
		y = True
	return x, y


def vector_change(x1, y1, x2, y2):
	return (x2 - x1, y2 - y1)


# x1, y1, x2, y2 is the outside box, x3, y3, x4, y4 is the inside box
def box_inside_box(x1, y1, x2, y2, x3, y3, x4, y4):
	if (x1 > x3 or y1 > y3):
		return False
	if (x2 < x4 or y2 < y4):
		return False
	return True
