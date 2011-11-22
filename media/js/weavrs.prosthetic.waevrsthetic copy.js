weavrs.previous_ajax_requests = [];

var v_canvas;

weavrs.initPage = function() {
	debug('Vomit running...');
	v_canvas = document.getElementById("vomitorium");
	weavrs.getConfiguration();
	};
	
var emotionArray = [];
var emotionInterval;
var configdataArray = [];
var configdataInterval = [];
var mapArray = [];
var mapInterval = [];
var locationArray = [];
var locationInterval = [];
var imageArray = [];
var imageInterval = [];
	
weavrs.getConfiguration = function () {
	debug('>>>>>>> WEAVRS GET CONFIGURATION OF THIS WEAVR FROM WEAVRS API');
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
	debug('>>>>>>> Got Configuration');
	// emotions and keywords
	$.each(data.emotions, function(i,e) {
		emotionArray.push(e.emotion);
		$.each(e.keywords, function(j,keyword) {
			emotionArray.push(keyword);
			});	
		});	
	emotionInterval = setInterval(drawEmotions, 50);
	// data
	configdataArray.push(data.id);
	configdataArray.push(data.last_modified_at);
	configdataArray.push(data.blog);
	configdataArray.push(data.date_of_birth);
	configdataArray.push(data.home_address);
	configdataArray.push(data.home_latlon);
	configdataArray.push(data.work_address);
	configdataArray.push(data.work_latlon);
	configdataArray.push(data.name);
	configdataArray.push(data.gender);
	configdataArray.push(data.work_latlon);
	debug(configdataArray);
	configdataInterval = setInterval(drawConfigdata, 100);
	// maps
	mapArray.push(data.home_address);
	mapArray.push(data.home_latlon);
	mapArray.push(data.work_address);
	mapArray.push(data.work_latlon);
	mapInterval = setInterval(drawMaps, 150);	
	weavrs.getLocations();
	}

weavrs.getLocations = function() {
	debug('>>>>>>> WEAVRS GET LOCATIONS FROM WEAVRS API');
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
	$.each(data.locations, function(i,location) {
		locationArray.push(location.lat+','+location.lon);
		});	
	debug(locationArray);
	locationInterval = setInterval(drawLocations, 125);
	weavrs.getPosts();
	}
	
weavrs.getPosts = function() {
	debug('>>>>>>> WEAVRS GET POSTS FROM WEAVRS API');
	var ajax_request_posts;
	ajax_request_posts = $.ajax({
		url: '/jswrapper/api/' + weavrs.weavr_name + '/post/',
		type: 'GET',
		//cache: false,
		data: "per_page = 100",
		dataType: 'json',
		success: weavrs.getPostsSuccess,
		error: weavrs.ajaxError,
		complete: weavrs.ajaxComplete
	});
	weavrs.previous_ajax_requests['get_locations'] = ajax_request_posts;
};

weavrs.getPostsSuccess = function(data, textStatus, jqXHR) {
	debug('>>>>>>> Got Posts');
	$.each(data.posts, function(i,post) {
		if (post.image_url) {
			imageArray.push(post.image_url);
			}
		});	
	debug(imageArray);
	imageInterval = setInterval(drawImages, 100);
	}
	
function drawEmotions() {
	var text = emotionArray.pop();
	if (text) {
		drawRandomText(text);
		}
	else {
		clearInterval(emotionInterval);
		}
	}
	
function drawConfigdata() {
	var text = configdataArray.pop();
	if (text) {
		drawRandomText2(text);
		}
	else {
		clearInterval(configdataInterval);
		}
	}
	
function drawMaps() {
	var ll = mapArray.pop();
	if (ll) {
		drawMap(ll);
		}
	else {
		clearInterval(mapInterval);
		}
	}
	
function drawLocations() {
	var ll = locationArray.pop();
	if (ll) {
		drawMap(ll);
		}
	else {
		clearInterval(mapInterval);
		}
	}
	
function drawImages() {
	var image = imageArray.pop();
	if (image) {
		drawImage(image);
		}
	else {
		clearInterval(imageInterval);
		}
	}
	
// All colors, sizes, fonts, 0.25 opacity...
function drawRandomText(text) {
	v_context = v_canvas.getContext("2d");
	v_context.globalAlpha = Math.floor(Math.random()*100) / 100;
	v_context.textBaseline = "middle";
	v_context.textAlign = "center";
	var fontsize = Math.floor(Math.random()*200) + 24;
	if (flipcoin() == 0) {	var fontweight = 'normal'; } else { var fontweight = 'bold'; }
	if (flipcoin() == 0) {	var fontstyle = 'serif'; } else { var fontstyle = 'sans-serif'; }
	v_context.font = fontweight+" "+fontsize+"px "+fontstyle;
	v_context.fillStyle = '#'+Math.floor(Math.random()*16777215).toString(16);
	var x = Math.floor(Math.random()*2000);
	var y = Math.floor(Math.random()*1500);
	v_context.fillText(text, x, y);
/* 	debug('> Writing to canvas: "'+text+'" '+fontweight+' '+fontsize+'px'+' '+fontstyle); */
	}

// greyscale, san-serif, bold, 0.75 opacity...	
function drawRandomText2(text) {
	v_context = v_canvas.getContext("2d");
	v_context.globalAlpha = Math.floor(Math.random()*100) / 100;
	v_context.textBaseline = "middle";
	v_context.textAlign = "center";
	var fontsize = Math.floor(Math.random()*200) + 24;
	v_context.font = "bold "+fontsize+"px sans-serif";
	var darkness = Math.floor(Math.random()*10);
	v_context.fillStyle = '#'+darkness+darkness+darkness;
	var x = Math.floor(Math.random()*2000);
	var y = Math.floor(Math.random()*1500);
	v_context.fillText(text, x, y);
/* 	debug('> Writing to canvas: "'+text+'" '+fontsize+'px #'+darkness+darkness+darkness); */
	}
	
function drawMap(latlon) {
	// random zoom level between 10 and 18
	var zoom = Math.floor(Math.random()*9) + 10;
	var width = Math.floor(Math.random()*401)+200;
	var height = Math.floor(Math.random()*401)+200;
	if (flipcoin() == 0) {	var maptype = 'satellite'; } else { var maptype = 'roadmap'; }
	var url = 'http://maps.googleapis.com/maps/api/staticmap?center='+latlon+'&zoom='+zoom+'&size='+width+'x'+height+'&maptype='+maptype+'&sensor=false';
	v_context = v_canvas.getContext("2d");
	v_context.globalAlpha = Math.floor(Math.random()*100) / 100;
	// top-left coord, within 2000x1500 square
	var x = Math.floor(Math.random()*(2000 - width));
	var y = Math.floor(Math.random()*(1500 - height));
	var staticmap = new Image();
  	staticmap.src = url;
  	staticmap.onload = function() {
  		v_context.drawImage(staticmap,x,y);
  		}
/* 	debug('> Drawing map to canvas: '+url); */
	}
	
function drawImage(url) {
	v_context = v_canvas.getContext("2d");
	v_context.globalAlpha = Math.floor(Math.random()*100) / 100;
	var img = new Image();
  	img.src = url;
	img.onload = function() {
		var x = Math.floor(Math.random()*(2000 - img.width));
		var y = Math.floor(Math.random()*(1500 - img.height));
  		v_context.drawImage(img,x,y);
  		}
	debug('> Drawing image to canvas: '+url);
	}
	
function flipcoin() {
	return Math.floor(Math.random() * 2);
	}
	
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
		}
	};