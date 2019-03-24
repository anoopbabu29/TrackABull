


def is_same_direction(x1, y2, x2, y2):
	x = False
	y = False
	if ((x1 < 0 and x2 < 0) or (x1 > 0 and x2 > 0) or (x1 == x2)):
		x = True
	if ((y1 < 0 and y2 < 0) or (y1 > 0 and y2 > 0) or (y1 == y2)):
		y = True
	return x, y


def vector_change(x1, y1, x2, y2):
	return (x2 - x1, y2 - y1)
