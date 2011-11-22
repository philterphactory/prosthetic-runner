weavrs.previous_ajax_requests = [];

$("#v_canvas").css('height',window.innerHeight-50);
$("#log_canvas").css('height',window.innerHeight-50);
$(window).resize(function() {
  	$("#v_canvas").css('height',window.innerHeight-50);
	$("#log_canvas").css('height',window.innerHeight-50);
	});

var log_canvas;
var log_context;
var log_interval;
var log_pointer = 0;
var log_buffer = [];

var v_canvas;
var v_context;

var text_buffer = [];
var text_x = 0;
var text_y = 0;

var image_buffer = [];

var counter_api = 0;
var counter_images = 0;
var counter_log = 0;
var counter_tags = 0;

weavrs.initPage = function() {
	log_canvas = document.getElementById("log_canvas");	
	v_canvas = document.getElementById("v_canvas");
	log_context = log_canvas.getContext("2d");
	v_context = v_canvas.getContext("2d");
	log_interval = setInterval(writeLog, 25);
	text_interval = setInterval(writeText, 100);
	image_interval = setInterval(writeImage, 150);
	updateCounter();
	logIt('running...');
	weavrs.getConfiguration();
	};
	
function logIt(text) {
	log_buffer.unshift(text);
	}	
function writeLog() {
	var text = log_buffer.pop();
	if (text) {
		// if log is greater than height (500 px = 50 lines), clear canvas, reset pointer
		if (log_pointer % 100 === 0 ) {
			log_context.save();
			log_context.setTransform(1, 0, 0, 1, 0, 0);
			log_context.clearRect(0, 0, log_canvas.width, log_canvas.height);
			log_context.restore();
			log_pointer = 0;
			}
		log_context.textBaseline = "top";
		log_context.textAlign = "left";
		log_context.font = "bold 5px sans-serif";		
		log_context.fillStyle = '#000';							
		log_context.fillText('>> '+text, 5, (5*log_pointer));
		log_pointer = log_pointer + 1;
		counter_log = counter_log+1;
		updateCounter();
		}
	}

// write tag text to the canvas
function writeText(){
	var text = text_buffer.pop();
	if (text) {
		v_context.globalAlpha = Math.floor(Math.random()*100) / 100;
		v_context.textBaseline = "middle";
		v_context.textAlign = "center";
		// FONT SIZE
		var fontsize = Math.floor(Math.random()*100) + 24;
		v_context.font = "bold "+fontsize+"px sans-serif";
		var darkness = Math.floor(Math.random()*10);
		v_context.fillStyle = '#'+darkness+darkness+darkness;
		if (flipcoin() == 0) {	
				text_x = text_x + (Math.random()*20) - 10;
				text_y = text_y + (Math.random()*20) - 10;
			} else { 
				if (flipcoin() == 0) {	
						text_x = text_x + (Math.random()*50) - 25;
						text_y = text_y + (Math.random()*50) - 25;
					} else {
						text_x = Math.floor(Math.random()*800);
						text_y  = Math.floor(Math.random()*500);
						}
				}
/*rgb text
		var standout = Math.floor(Math.random()*500);
		if (standout == 100) {
			v_context.fillStyle = '#f00';
			v_context.globalAlpha = 0.8;
			}
		else if (standout == 99) {
			v_context.fillStyle = '#0f0';
			v_context.globalAlpha = 0.8;
			}
		else if (standout == 98) {
			v_context.fillStyle = '#00f';
			v_context.globalAlpha = 0.8;
			}
*/
		v_context.fillText(text, text_x, text_y);
		counter_tags = counter_tags+1;
		updateCounter();
		}
	}
// take a location, either a latlong or an address
// build a new gmaps static url with height/width between 200 and 450 px.
// push the url to the image buffer
function writeLocation(location) {
	var zoom = Math.floor(Math.random()*9) + 10;
	if (flipcoin() == 0) {	var maptype = 'satellite'; } else { var maptype = 'roadmap'; }
	var width = Math.floor(Math.random()*251)+200;
  	var height = Math.floor(Math.random()*251)+200;
	var url = 'http://maps.googleapis.com/maps/api/staticmap?center='+location+'&zoom='+zoom+'&size='+width+'x'+height+'&maptype='+maptype+'&sensor=false';
	image_buffer.unshift(url);
	}

// draw the image buffer to v_context
// randomise image size between 200px and full height/width.
// place in random location within context so whole image fits
function writeImage(){
	var url = image_buffer.pop();
	if (url) {
		var img = new Image();	
	 	img.src = url;
  		img.onload = function() {	
  			v_context.globalAlpha = Math.floor(Math.random()*75) / 100;
			// size of clipped image
			var dw = Math.floor(Math.random()*(img.width));
			var dh = Math.floor(Math.random()*(img.height));
			// origin of clip
			var sx = Math.floor(Math.random()*(img.width - dw));
			var sy = Math.floor(Math.random()*(img.width - dh));
			// size of clip again (no stretching)
			var sw = dw;
			var sh = dh;
			// placement of clip
			var dx = Math.floor(Math.random()*(801-img.width));
			var dy = Math.floor(Math.random()*(501-img.height));
			// draw it
			v_context.drawImage(img, sx, sy, sw, sh, dx, dy, dw, dh);
			counter_images = counter_images+1;
			updateCounter();
			}
		}
	}
	
weavrs.getConfiguration = function () {
	debug('>>>>>>> WEAVRS GET CONFIGURATION OF THIS WEAVR FROM WEAVRS API');
	logIt('calling configuration...');
	counter_api = counter_api+1;
	updateCounter();
	var ajax_request_config;
	ajax_request_config = $.ajax({
		url: '/jswrapper/api/' + weavrs.weavr_name + '/configuration/',
		type: 'GET',
		//cache: false,
		dataType: 'json',
		success: weavrs.getConfigurationSuccess,
		error: weavrs.ajaxError,
		complete: weavrs.ajaxComplete
		});	
	weavrs.previous_ajax_requests['get_configuration'] = ajax_request_config;
	};
weavrs.getConfigurationSuccess = function(data, textStatus, jqXHR) {
	logIt('received configuration');
	// emotions and keywords
	logIt('id: '+data.id);
	logIt('last_modified_at: '+data.last_modified_at);
	logIt('blog: '+data.blog);
	logIt('date_of_birth: '+data.date_of_birth);
	logIt('PRINT '+'home_latlon: '+data.home_latlon);
	writeLocation(data.home_latlon);
	logIt('PRINT '+'work_address: '+data.work_address);
	writeLocation(data.home_latlon);
	logIt('PRINT '+'work_latlon: '+data.home_latlon);
	writeLocation(data.home_latlon);
	logIt('name: '+data.name);
	logIt('gender: '+data.gender);
	logIt('PRINT '+'work_latlon: '+data.work_latlon);
	writeLocation(data.work_latlon);
	$.each(data.emotions, function(i,e) {
		logIt('emotion: '+e.emotion);
		$.each(e.keywords, function(j,keyword) {
			text_buffer.unshift(keyword);
			logIt('PRINT '+e.emotion+' keyword: '+keyword)
			});	
		});	
	weavrs.getLocations();
	}
	
weavrs.getLocations = function() {
	debug('>>>>>>> WEAVRS GET LOCATIONS FROM WEAVRS API');
	logIt('calling locations...');
	counter_api = counter_api+1;
	updateCounter();
	var ajax_request_locations;
	ajax_request_locations = $.ajax({
		url: '/jswrapper/api/' + weavrs.weavr_name + '/location/',
		type: 'GET',
		//cache: false,
		dataType: 'json',
		success: weavrs.getLocationsSuccess,
		error: weavrs.ajaxError,
		complete: weavrs.ajaxComplete
	});
	weavrs.previous_ajax_requests['get_locations'] = ajax_request_locations;
};
weavrs.getLocationsSuccess = function(data, textStatus, jqXHR) {
	debug('>>>>>>> Got Locations');
	logIt('received locations...');
	$.each(data.locations, function(i,location) {
		logIt('location: '+location.lat+','+location.lon);
		writeLocation(location.lat+','+location.lon);
		});	
	weavrs.getPalettePosts();
	}
	
weavrs.getPalettePosts = function() {
	debug('>>>>>>> WEAVRS GET PALETTE POSTS FROM WEAVRS API');	
	logIt('calling palettes...');
	counter_api = counter_api+1;
	updateCounter();
	var ajax_request_posts;
	ajax_request_posts = $.ajax({
		url: '/jswrapper/api/' + weavrs.weavr_name + '/post/',
		type: 'GET',
		//cache: false,
		data: "category=palette",
		dataType: 'json',
		success: weavrs.getPalettePostsSuccess,
		error: weavrs.ajaxError,
		complete: weavrs.ajaxComplete
		});
	weavrs.previous_ajax_requests['get_locations'] = ajax_request_posts;
	};
weavrs.getPalettePostsSuccess = function(data, textStatus, jqXHR) {
	debug('>>>>>>> Got Palettes');
	logIt('received palettes...');
	$.each(data.posts, function(i,post) {
		logIt('run time '+post.run);
		logIt('post title '+post.title);
		logIt('post url '+post.blog_post_url);
		logIt('post id: '+post.id);
/*
		if (i==1) {
			var palette = new Image();
  			palette.src = post.image_url;
  			palette.onload = function() {
  				v_context.globalAlpha = 0.75;
  				v_context.drawImage(palette,0,0,800,500);
  				}
			logIt('PRINT: palette '+post.image_url);
			}
*/
		});	
		weavrs.getImagePosts();
	}

weavrs.getImagePosts = function() {
	debug('>>>>>>> WEAVRS GET IMAGE POSTS FROM WEAVRS API');	
	logIt('calling images...');
	counter_api = counter_api+1;
	updateCounter();
	var ajax_request_posts;
	ajax_request_posts = $.ajax({
		url: '/jswrapper/api/' + weavrs.weavr_name + '/post/',
		type: 'GET',
		//cache: false,
		data: "category=image",
		dataType: 'json',
		success: weavrs.getImagePostsSuccess,
		error: weavrs.ajaxError,
		complete: weavrs.ajaxComplete
		});
	weavrs.previous_ajax_requests['get_locations'] = ajax_request_posts;
	};
weavrs.getImagePostsSuccess = function(data, textStatus, jqXHR) {
	debug('>>>>>>> Got Images');
	logIt('received images...');
	$.each(data.posts, function(i,post) {
		logIt('run time '+post.run);
		logIt('post title '+post.title);
		logIt('post url '+post.blog_post_url);
/* Keywords actually a bit overwhelming
		$.each(post.keywords.split(" "), function(j,postkeyword) {
			text_buffer.unshift(postkeyword);
			logIt('PRINT post keyword: '+postkeyword);
			});
*/
		logIt('post id: '+post.id);
		if (post.image_url) {
			image_buffer.push(post.image_url);
			logIt('PRINT: image '+post.image_url);
			}
		});	
	logIt('LOOPING');	
	weavrs.getConfiguration();
	}

function updateCounter() {
	log_context.clearRect(648,478,155,14);	
	log_context.fillStyle = '#666';
	log_context.fillRect(648,478,155,14);
	log_context.textBaseline = "bottom";
	log_context.textAlign = "right";
	log_context.font = "normal 8px sans-serif";
	log_context.fillStyle = '#999';
	log_context.fillText('log'+counter_log+'apicall'+counter_api+'image'+counter_images+'tag'+counter_tags, 790, 490);	
	}
	
function flipcoin() {
	return Math.floor(Math.random() * 2);
	}

function glitchImage(img){
		var iw = img.width;
		var ih = img.height;
		//draw input image to output canvas
		outputBMD = new BitmapData(iw, ih);
		outputBMD.draw(img);
		//init inputBMD
		inputBMD = new BitmapData(iw, ih);
		inputBMD.draw(img);
		var _glitchAmount = 5;
		var maxOffset = _glitchAmount * _glitchAmount / 100 * iw;
		//randomly offset slices horizontally
		for (i = 0; i < _glitchAmount * 2; i++) {
			var startY = getRandInt(0, ih);
			var chunkHeight = getRandInt(1, ih / 4);
			chunkHeight = Math.min(chunkHeight, ih - startY);
			var offset = getRandInt(-maxOffset, maxOffset);
			if (offset == 0)
				continue;
			if (offset < 0) {
				//shift left
				outputBMD.copyPixels(inputBMD, new Rectangle(-offset, startY, iw + offset, chunkHeight), new Point(0, startY));
				//wrap around
				outputBMD.copyPixels(inputBMD, new Rectangle(0, startY, -offset, chunkHeight), new Point(iw + offset,startY));
			} else {
				//shuft right
				outputBMD.copyPixels(inputBMD, new Rectangle(0, startY, iw, chunkHeight), new Point(offset, startY));
				//wrap around
				outputBMD.copyPixels(inputBMD, new Rectangle(iw - offset, startY, offset, chunkHeight), new Point(0, startY));
				}
			}
		//do color offset
		var channel = getRandChannel();
		outputBMD.copyChannel(inputBMD, new Rectangle(0, 0, iw, ih), new Point(getRandInt(-_glitchAmount * 2, _glitchAmount * 2), getRandInt(-_glitchAmount * 2, _glitchAmount * 2)), channel, channel);
		//make brighter
		var brightMat=[
										2, 0, 0, 0, 0,
										0, 2, 0, 0, 0,
										0, 0, 2, 0, 0,
										0, 0, 0, 1, 0
									 ];
		zeroPoint = new Point();
		brightnessFilter = new ColorMatrixFilter(brightMat);
		outputBMD.applyFilter(outputBMD, outputBMD.rect, zeroPoint, brightnessFilter);
		//Add Scan Lines
		var line = new Rectangle(0, 0, iw, 1);
		for (i = 0; i < ih; i++) {
			if (i % 2 == 0) {
				line.y = i;
				outputBMD.fillRect(line, 0);
				}
			}
	// return img
	return outputBMD.data;
	};
function getRandInt(min, max) {
	return (Math.floor(Math.random() * (max - min) + min));
	}
function getRandChannel() {
	var r = Math.random();
	if (r < .33){
		return BitmapDataChannel.GREEN;
	}else if (r > .33 && r < .66){
		return BitmapDataChannel.RED;
	}else{
		return BitmapDataChannel.BLUE;
		}
	}

$("#snapshot").click( function() {
	//open canvas image in new tab
	window.open(document.getElementById("v_canvas").toDataURL());
	});

//=================================

weavrs.ajaxError = function (jqXHR, textStatus, errorThrown) {
	debug(textStatus);
	debug(errorThrown);
	$('textarea', this).val(JSON.stringify(data));
	};

weavrs.ajaxComplete = function (jqXHR, textStatus) {
	switch (textStatus) {
		case "success":
		case "notmodified":
		case "error":
		case "timeout": 
		case "abort":
		case "parsererror":
		default:
			debug(textStatus);
			logIt(textStatus);
		}
	};