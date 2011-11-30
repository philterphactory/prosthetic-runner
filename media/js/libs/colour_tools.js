/**
* Converts hexidecimal string to RGB object.
*/
function hexToRgb(hex){
	var r = (hex & 0xff0000) >> 16,
		g = (hex & 0x00ff00) >> 8,
		b = hex & 0x0000ff;

	return {r:r, g:g, b:b};
}

/**
* rgb to hex 
*/
function rgbToHex(r, g, b) {
	return ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

/**
* Converts HSV to RGB value.
*
* @param {Integer} h Hue as a value between 0 - 360 degrees
* @param {Integer} s Saturation as a value between 0 - 100 %
* @param {Integer} v Value as a value between 0 - 100 %
* @returns {Array} The RGB values  EG: [r,g,b], [255,255,255]
*/
function hsvToRgb(h,s,v) {

	var s = s / 100,
		v = v / 100,

		hi = Math.floor((h / 60) % 6),
		f = (h / 60) - hi,
		p = v * (1 - s),
		q = v * (1 - f * s),
		t = v * (1 - (1 - f) * s),

		rgb = [];

	switch (hi) {
		case 0: rgb = [v,t,p];break;
		case 1: rgb = [q,v,p];break;
		case 2: rgb = [p,v,t];break;
		case 3: rgb = [p,q,v];break;
		case 4: rgb = [t,p,v];break;
		case 5: rgb = [v,p,q];break;
	}

	return {r:Math.min(255, Math.round(rgb[0] * 256)),
			g:Math.min(255, Math.round(rgb[1] * 256)),
			b:Math.min(255, Math.round(rgb[2] * 256))};
}	

/**
* Converts RGB to HSV value.
*
* @param {Integer} r Red value, 0-255
* @param {Integer} g Green value, 0-255
* @param {Integer} b Blue value, 0-255
* @returns {Array} The HSV values EG: [h,s,v], [0-360 degrees, 0-100%, 0-100%]
*/
function rgbToHsv(r, g, b) {

	var r = (r / 255),
		g = (g / 255),
		b = (b / 255),

		min = Math.min(Math.min(r, g), b),
		max = Math.max(Math.max(r, g), b),
		delta = max - min,

		value = max,
		saturation,
		hue;

	// Hue
	if (max == min) {
		hue = 0;
	} else if (max == r) {
		hue = (60 * ((g-b) / (max - min))) % 360;
	} else if (max == g) {
		hue = 60 * ((b - r) / (max - min)) + 120;
	} else if (max == b) {
		hue = 60 * ((r - g) / (max - min)) + 240;
	}

	if (hue < 0) {
		hue += 360;
	}

	// Saturation
	if (max == 0) {
		saturation = 0;
	} else {
		saturation = 1 - (min / max);
	}

	return {h:Math.round(hue), 
			s:Math.round(saturation * 100),
			v:Math.round(value * 100)};
}
