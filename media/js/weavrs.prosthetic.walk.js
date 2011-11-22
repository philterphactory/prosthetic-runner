// BASED ON CODE FROM http://gmaps-samples.googlecode.com/svn/trunk/streetview/streetview_directions.html

weavrs.streetview = false;

weavrs.map = false;

weavrs.progress_marker = false;

weavrs.previous_ajax_requests = {};

weavrs.maps_api_key = 'ABQIAAAAlZ4VE7rnI9OiJknNV6vobxROU4PuzPG2t-KTI8G2aUsstI59mxR1XC1OsfUjG6jo_pqp1E9U2SspHw';

weavrs.destinations = false;

weavrs.current_destination_index = 0;

weavrs.current_destination = false;

weavrs.sv_client = false;

weavrs.greetings = ['Hey', 'Hi', 'Hello', 'Heya'];

/**
* The GRoute we are following extracted from the directions response.
*/
weavrs.route = false;

/**
* It turns out that the polyline generated for a walking directions
* route normally has a lot of repeated vertices. This causes problems
* when trying to determine how close we are to the next vertex, so it's
* better to collapse these duplicated vertices out.
*
* The array of route vertices with duplicates removed.
*/
weavrs.vertices = false;

/**
* Array that maps the polyline vertex indices to the
* index of the same point in the vertices array.
*
* For example, if the polyline vertices are
* [a, a, b, c, d, d, e], the vertices array will be
* [ a, b, c, d, e ] and the vertexMap array will be
* [ 1, 1, 2, 3, 4, 4, 5 ].
*/
weavrs.vertex_map = false;

/**
* Array that contains the index in the vertices array of
* the point at the start of the n'th step in the route
*/
weavrs.step_to_vertex = false;

/**
* An array that gives the route step number that each
* point in the vertices array is part of.
*/
weavrs.step_map = false;

/**
* The current position of the panorama and vehicle marker.
*/
weavrs.current_vertex = false;

/**
* Metadata for the current panorama including the list of
* available links, loaded using GStreetviewClient.
*/
weavrs.pano_meta_data = false;

/**
* boolean flag set when we are so close to the next vertex that we should
* check links in the panoramas we load for the next turning we need.
*/
weavrs.close_to_next_vertex = false;

/**
* The direction in degrees from our current location to the next
* vertex on the route. Used to select the most suitable link to follow.
*/
weavrs.bearing = false;

/**
* Currently selected street view link within the current panorama
*/
weavrs.selected_link = false;

/**
* Street view link within the current panorama that is in the direction the weavrs need to turn next
*/
weavrs.selected_turn = false;

/**
* The direction from the next vertex on the route to the vertex
* after that. Used when we are close to a vertex and are looking
* for links that represent the next turn we need to make.
*/
weavrs.next_bearing = false;

/**
* The index of the vertex we are heading towards on the route in the
* vertices array.
*/
weavrs.next_vertex_index = false;

/**
* GLatLng of the vertex we are heading towards on the route.
*/
weavrs.next_vertex = false;

/**
* An array that at any time contains the GLatLng of each vertex
* from the start of the current route step to the next vertex
* ahead of our current position. This is used to work out how
* far we are along the current step.
*/
weavrs.progress_array = false;

/**
* The distance in meters covered by traversing the points in the
* progressArray. By subtracting the distance from our current location
* to the next vertex from this value we find how far along the step
* we are, and use this to update the progress bar.
*/
weavrs.progress_distance = false;

/**
* Index of the route step we are currently on.
*/
weavrs.current_step = false;


/**
* boolean flag indicating whether we are currently walking (automatically
* following) links, or are stationary.
*/
weavrs.moving = false;

/**
* Id of the timer that adds a delay between following each link to give the
* panorama time to load. We need this to cancel the timer if the user clicks
* Stop while we are waiting to follow the next link.
*/
weavrs.advance_timer = null;

/**
* Delay in seconds between following each link.
*/
weavrs.advance_delay = 1;

/*
* list of all weavrs within a set radius to the current destination
*/
weavrs.nearby = [];

weavrs.nearby_weavrs_hello_proximity_threshold = 1000;


weavrs.nearby_weavr_saying_hello = false;


/*
* configuration of weavr being viewed - retrieved from the weavrs api
*/
weavrs.weavr_configuration = false;

/*
* prepended to the destination titles
*/ 
weavrs.destination_phrases = ['On my way to ', 'Heading for ', 'Walking to ', 'Going to '];

/*
* delay used to hide the weavrs info after no mouse movement
*/
weavrs.showInfoTimeout = false;




// called from the LABjs process at the bottom of the base template
weavrs.initPage = function() {
	debug('>>>>>>>WEAVRS INITIALIZING WEAVRS ROUTE WALKING');
	weavrs.getConfiguration();
};


weavrs.getConfiguration = function () {
	debug('>>>>>>>WEAVRS GET CONFIGURATION OF THIS WEAVR FROM WEAVRS API');
	var ajax_request;

	ajax_request = $.ajax({
		url: '/jswrapper/api/' + weavrs.weavr_name + '/configuration/',
		type: 'GET',
		//cache: false,
		dataType: 'json',
		success: weavrs.getConfigurationSuccess,
		error: weavrs.ajaxError,
		complete: weavrs.ajaxComplete
	});
	
	weavrs.previous_ajax_requests.get_configuration = ajax_request;
};


weavrs.getConfigurationSuccess = function (data, textStatus, jqXHR) {
	debug('>>>>>>>WEAVRS GET CONFIGURATION SUCCESS');
	debug(textStatus);
	debug(data);

	weavrs.weavr_configuration = data;
	
	$('#main-weavrs-info .avatar').attr('src', weavrs.hub_url + 'api/weavrs/' + weavrs.weavr_configuration.id + '/avatar_current_image.png');
	$('#main-weavrs-info h1.fn a, #main-weavrs-info .outgoing .fn a').html(weavrs.weavr_name.replace(/(_|-)/,' '));
	
	weavrs.getLocations();
};


weavrs.getLocations = function() {
	debug('>>>>>>>WEAVRS GET LOCATIONS FROM WEAVRS API');
	var ajax_request;

	ajax_request = $.ajax({
		url: '/jswrapper/api/' + weavrs.weavr_name + '/location/',
		type: 'GET',
		//cache: false,
		dataType: 'json',
		success: weavrs.getLocationsSuccess,
		error: weavrs.ajaxError,
		complete: weavrs.ajaxComplete
	});
	
	weavrs.previous_ajax_requests.get_locations = ajax_request;
};


weavrs.getLocationsSuccess = function (data, textStatus, jqXHR) {
	debug('>>>>>>>WEAVRS GET LOCATIONS SUCCESS');
	debug(textStatus);
	debug(data);

	weavrs.destinations = data.locations.reverse();
	weavrs.current_destination_index = 0;
	weavrs.current_destination = weavrs.destinations[0];
	weavrs.getNearByWeavrsLocations(weavrs.current_destination.lat, weavrs.current_destination.lon, 10000);
};


weavrs.getNearByWeavrsLocations = function (lat, lon, radius) {
	debug('>>>>>>>WEAVRS GET LOCATIONS OF OTHER NEAR BY WEAVRS FROM WEAVRS API');
	var ajax_request;
	ajax_request = $.ajax({
		url: weavrs.hub_url + 'api/layar/?lat=' + lat + '&lon=' + lon + '&radius=' + radius,
		type:'GET',
		crossDomain:true,
		//cache: false,
		dataType:'jsonp',
		success:weavrs.getNearByWeavrsLocationsSuccess,
		error:weavrs.ajaxError,
		complete:weavrs.ajaxComplete
	});
	
	weavrs.previous_ajax_requests.get_near_by_weavrs_locations = ajax_request;
};


weavrs.getNearByWeavrsLocationsSuccess = function (data, textStatus, jqXHR) {
	debug('>>>>>>>WEAVRS GET NEAR BY WEAVRS LOCATIONS SUCCESS');
	debug(textStatus);
	debug(data);

	weavrs.nearby = data.hotspots;

	weavrs.initMap();
};


weavrs.initMap = function(lat,lon) {
	debug('>>>>>>>WEAVRS INIT MAP');
	var i, copy_of_weavrs_nearby, custom_ui,
		gLatlng = new GLatLng(weavrs.current_destination.lat, weavrs.current_destination.lon);
	
	weavrs.current_vertex = gLatlng;
	
	weavrs.map = new GMap2(document.getElementById("map"));
	weavrs.map.setCenter(gLatlng);
	weavrs.map.setZoom(12);

	custom_ui = weavrs.map.getDefaultUI();
	custom_ui.controls = false;
	weavrs.map.setUI(custom_ui);
	
	weavrs.progress_marker = weavrs.getProgressMarker(weavrs.current_vertex);
	weavrs.map.addOverlay(weavrs.progress_marker);
	weavrs.progress_marker.hide();
	
	weavrs.resizeView();
	
	weavrs.streetview = new GStreetviewPanorama(document.getElementById("streetview"), {
		latlng:gLatlng,
		navigationControl:false,
		features: {
			streetView:true,
			userPhotos:false,
			enableCloseButton:false}
	});
	
	copy_of_weavrs_nearby = [];

	$.each(weavrs.nearby, function(index, weavr) {
		// exclude current and empty/malformed weavrs from the list of nearby weavrs
		if (weavr.user != weavrs.weavr_name && weavr.user.length > 1) {
			copy_of_weavrs_nearby.push(weavr);
		}
	});
	
	weavrs.nearby = $.extend(true, [], copy_of_weavrs_nearby);

	$.each(weavrs.nearby, function(index, weavr) {
		// reverse the lat/lng * 1000000 that is applied for the benefit of the layar api
		if (typeof weavr.lat != 'undefined') {
			weavrs.nearby[index].lat *= 0.000001;
		}
		if (typeof weavr.lon != 'undefined') {
			weavrs.nearby[index].lon *= 0.000001;
		}
		weavrs.nearby[index].said_hello_already = false;
		var gLatLng = new GLatLng(weavrs.nearby[index].lat, weavrs.nearby[index].lon);
		var m = new GMarker(gLatLng, {title: weavrs.nearby[index].attribution});
		weavrs.map.addOverlay(m);
		debug(weavr.lat + ', ' + weavr.lon);
	});
	
	weavrs.sv_client = new GStreetviewClient();
	
	weavrs.directions = new GDirections(weavrs.map);
	
	GEvent.addListener(weavrs.streetview, 'error', function (errCode) {
		debug('error: streetview panorama for this location could not be found');
		debug(errCode);
	});
	
	GEvent.addListener(weavrs.streetview, "initialized", function (location) {
		debug('sv initialized event');
		/*
		* significantly this is triggered when a link step within the current panarama has been panned to 
		* and the panorama is loaded fully - at which point the next link needs to be selected by invoking the move process
		*/
		debug(location);
		if (weavrs.moving) {
			weavrs.pano_meta_data = location;
			if (weavrs.bearing) {
				weavrs.pano_meta_data.pov.yaw = weavrs.bearing;
			}
			weavrs.move();
		}
	});
	
	GEvent.addListener(weavrs.directions, "load", function () {
		weavrs.setOffOnJourney();
	});
	
	GEvent.addListener(weavrs.directions, "addoverlay", function () {
		debug('>>>>>>>WEAVRS DIRECTIONS ADDOVERLAY');
	});
	
	$(window).bind('resize', function () {
		weavrs.resizeView();
		weavrs.streetview.checkResize();
	});
	
	// show weavrs info overlay if not visible or fading in already
	$('body').mousemove(function(e) {
		if($('#main-weavrs-info').attr('state') != 'visible' && $('#main-weavrs-info').attr('state') != 'fading-in') {
			weavrs.showInfo();
		}
		
		clearTimeout(weavrs.showInfoTimeout);
		
		//weavrs.showInfoTimeout = setTimeout(function () {weavrs.hideInfo();}, 2000);
	});
	
	// when called from here the first location returned from the weavrs api is used as the current_vertex 
	// and the second as the first target current_destination, and the route is plotted between the two
	weavrs.nextDestination();
};


weavrs.resizeView = function () {
	$('#streetview').height($(window).height() - 50);
};


weavrs.nextDestination = function () {
	debug('>>>>>>>WEAVRS SWITCHING TO NEXT DESTINATION');
	
	weavrs.current_destination_index += 1;
	
	if (weavrs.current_destination_index >= weavrs.destinations.length) {
		//for now just loop initial locations - todo - add pagination/fetching of next locations from api
		weavrs.current_destination_index = 0;
	}

	weavrs.current_destination = weavrs.destinations[weavrs.current_destination_index];

	
	var d = new Date(weavrs.current_destination.date);
	$('#main-weavrs-info time').attr('datetime', weavrs.current_destination.date);
	$('#main-weavrs-info .date').html(d.toDateString());
	$('#main-weavrs-info .time').html(d.toTimeString());
	$('#main-weavrs-info .title').html(weavrs.destination_phrases[Math.floor(Math.random() * weavrs.destination_phrases.length)] + weavrs.current_destination.title);
	$('#main-weavrs-info .address').html(weavrs.current_destination.street_address + ', ' + weavrs.current_destination.city + ', ' + weavrs.current_destination.country);

	weavrs.showInfo();
	
	weavrs.getDirections();
};


weavrs.showInfo = function () {
	$('#main-weavrs-info').stop().attr('data-state','fadding-in').fadeTo(200,1, function () {
		$(this).attr('state','visible');
	});
};


weavrs.hideInfo = function () {
	$('#main-weavrs-info').stop().attr('data-state','fadding-out').fadeTo(1000,0, function () {
		$(this).attr('state','hidden');
	});
};


/**
* Submit the walking directions request
* The load event callback handler calls setOffOnJourney()
*/ 
weavrs.getDirections = function () {
	debug('>>>>>>>WEAVRS GET DIRECTIONS');
	var from = weavrs.current_vertex.lat() + ',' + weavrs.current_vertex.lng(),
		to = weavrs.current_destination.lat + ',' + weavrs.current_destination.lon;
		
	weavrs.directions.load("from: " + from + " to: " + to, { preserveViewport: true, getSteps: true });
};


/**
* Weavrs get going
*/ 
weavrs.setOffOnJourney = function () {
	debug('>>>>>>>WEAVRS SET OFF ON JOURNEY');
	/* Extract the one and only route from this response */
	weavrs.route = weavrs.directions.getRoute(0);
	
	/* Simplify the list of polyline vertices by removing duplicates */
	weavrs.collapseVertices(weavrs.directions.getPolyline());
	
	/* Center the map on the start of the route at street level */
	weavrs.map.setCenter(weavrs.vertices[0], 13);
	
	/* Begin checking the Street View coverage along this route */
	weavrs.checkSVCoverage(0);
};


/**
* Build the vertices, vertexMap, stepToVertex, and stepMap
* arrays from the vertices of the route polyline.
* @param {GPolyline} path The route polyline to process
*/
weavrs.collapseVertices = function (path) {
	debug('>>>>>>>WEAVRS COLLAPSE VERTICES');
	debug(path);
	var i, step, path_vertex_count = path.getVertexCount();
	debug('path_vertex_count=' + path_vertex_count);
	if (path_vertex_count < 2) {
		// current destination too close to current location
		// so select next destination
		weavrs.nextDestination();
		return false;
	}
	weavrs.vertices = new Array();
	weavrs.vertex_map = new Array(path.getVertexCount());
	
	weavrs.vertices.push(path.getVertex(0));
	weavrs.vertex_map[0] = 0;

	/* Copy vertices from the polyline to the vertices array
	* skipping any duplicates. Build the vertexMap as we go along */
	for (var i = 1; i < path_vertex_count; i++) {
		if ( ! path.getVertex(i).equals(weavrs.vertices[weavrs.vertices.length - 1])) {
			weavrs.vertices.push(path.getVertex(i));
		}
		weavrs.vertex_map[i] = weavrs.vertices.length - 1;
	}
	
	weavrs.step_to_vertex = new Array(weavrs.route.getNumSteps());
	weavrs.step_map  	= new Array(weavrs.vertices.length);
	
	for (i = 0; i < weavrs.route.getNumSteps(); i++) {
		weavrs.step_to_vertex[i] = weavrs.vertex_map[weavrs.route.getStep(i).getPolylineIndex()];
	}
	
	step = 0;
	for (i = 0; i < weavrs.vertices.length; i++) {
		if (weavrs.step_to_vertex[step + 1] == i) {
			step++;
		}
		weavrs.step_map[i] = step;
	}
	
	debug('vertices=');
	debug(weavrs.vertices);
	debug(weavrs.vertex_map);
	debug('verticex steps=');
	debug(weavrs.step_to_vertex);
	debug(weavrs.step_map);
};


/**
* Check that a Street View panorama exists at the start
* of this route step. This is a recursive function that
* checks every step along the route until it reaches the
* end of the route or no panorama is found for a step.
* @param {number} step The route step to check
*/ 
weavrs.checkSVCoverage = function (step) {
	debug('>>>>>>>WEAVRS CHECK STREET VIEW COVERAGE');
	if (step > weavrs.route.getNumSteps()) {
		/* Coverage check across whole route passed */
		//weavrs.stopMoving();
		weavrs.moving = true;
		weavrs.jumpToVertex(0);
	} else {
		if (step == weavrs.route.getNumSteps()) {
			gLatLng = weavrs.route.getEndLatLng();
		} else {
			gLatLng = weavrs.route.getStep(step).getLatLng();
		}

		weavrs.sv_client.getNearestPanorama(gLatLng, function(sv_data) {
			if (sv_data.code == 500) {
				/* Server error, retry once per second */
				setTimeout(function () {weavrs.checkSVCoverage(step);}, 1000);
				return false;
			} else if (sv_data.code == 600) {
				/* Coverage check failed */
				debug("checkSVCoverage error 600 : Street View coverage is not available for this route");
			}
			/* Confirmed coverage for this step.
			* Now check coverage for next step.
			*/
			weavrs.checkSVCoverage(step + 1);
		});
	}
};


/**
* Update the UI for walking and start following links
*/
weavrs.startMoving = function () {
	debug('>>>>>>>WEAVRS START MOVING');
	weavrs.moving = true;
	weavrs.move();
};


/**
* Stop following links and update the UI
*/
weavrs.stopMoving = function () {
	debug('>>>>>>>WEAVRS STOP MOVING');
	weavrs.moving = false;
	
	if (weavrs.advance_timer != null) {
		clearTimeout(weavrs.advance_timer);
		weavrs.advance_timer = null;
	}
};


/**
* Jump to a particular point on the route. This is used to
* queue up the start of the route and when there is a gap in street view coverage
* that weavrs need to jump over.
* @param {number} vertex_index The vertex number in the vertices array
*/ 
weavrs.jumpToVertex = function (vertex_index) {
	debug('>>>>>>>WEAVRS JUMP TO VERTEX');
	
	if ( ! weavrs.vertices[weavrs.next_vertex_index + 1]) {
		/* we are at the end of the route */
		weavrs.destinationReached();
		return false;
	}
	
	weavrs.current_vertex = weavrs.vertices[vertex_index];
	weavrs.next_vertex = weavrs.vertices[vertex_index + 1];
	weavrs.next_vertex_index = vertex_index + 1;
	
	weavrs.bearing = weavrs.getBearingFromVertex(vertex_index);
	weavrs.next_bearing = weavrs.getBearingFromVertex(vertex_index + 1);
	
	weavrs.setProgressMarkerImage(weavrs.bearing);
	weavrs.progress_marker.setLatLng(weavrs.current_vertex);
	weavrs.progress_marker.show();
	
	weavrs.current_step = weavrs.step_map[vertex_index];
	
	debug(weavrs.current_vertex);
	debug(weavrs.next_vertex);
	debug(weavrs.next_vertex_index);
	debug(weavrs.bearing);
	debug(weavrs.next_bearing);
	debug(weavrs.step_map);
	debug(weavrs.current_step);
	
	weavrs.constructProgressArray(vertex_index);
	weavrs.setProgressDistance();
	
	weavrs.map.panTo(weavrs.current_vertex, 13);
	weavrs.checkDistanceFromNextVertex();
	
	weavrs.streetview.setLocationAndPOV(weavrs.current_vertex, { yaw: weavrs.bearing, pitch: 0 });
	
	weavrs.sv_client.getNearestPanorama(weavrs.current_vertex, function(sv_data) {
		if (sv_data.code == 500) {
			setTimeout(function () {weavrs.jumpToVertex(vertex_index);}, 1000);
		} else if (sv_data.code == 600) {
			debug('no streetview for location:');
			debug(sv_data);
			setTimeout(function () {weavrs.jumpToVertex(weavrs.next_vertex_index);}, 1000);
		} else {
			debug('found streetviw for location:');
			debug(sv_data);
			weavrs.pano_meta_data = sv_data.location;
			weavrs.pano_meta_data.pov.yaw = weavrs.bearing;
			weavrs.move();
		}
	});
};


/**
* Called by the panorama's initialized event handler in
* response to a link being followed. Updates the location
* of the vehicle marker and the center of the map to match
* the location of the panorama loaded by following the link.
*/ 
weavrs.move = function () {
	debug('>>>>>>>WEAVRS MOVE');
	weavrs.current_vertex = weavrs.pano_meta_data.latlng;
	weavrs.map.panTo(weavrs.current_vertex, 13);
	weavrs.progress_marker.setLatLng(weavrs.current_vertex);

	weavrs.sv_client.getNearestPanorama(weavrs.pano_meta_data.latlng, function(sv_data) {
		if (sv_data.code == 500) {
			/* Server error. Retry once a second */
			setTimeout(function () {weavrs.getStreetViewLinks();}, 1000);
		} else if (sv_data.code == 600) {
			/* No panorama. Should never happen as we have
			* already loaded this panorama in the Flash viewer.
			*/
			weavrs.jumpToVertex(weavrs.next_vertex_index);
		} else {
			debug('weavrs.pano_meta_data.links=');
			debug(sv_data.links);
			if (typeof sv_data.links != 'undefined') {
				if (sv_data.links.length) {
					weavrs.pano_meta_data.links = sv_data.links;
					weavrs.checkDistanceFromNextVertex();
					weavrs.advance_timer = setTimeout(function () {weavrs.advance();}, weavrs.advance_delay * 1000);
					return true;
				}
			}
			debug('no steetview jump links available for linking to in the immediate panorama');
			weavrs.jumpToVertex(weavrs.next_vertex_index);
			return false;
		}
	});
	
	weavrs.nearByWeavrsSayHello();
};


weavrs.nearByWeavrsSayHello = function () {
	debug('>>>>>>>WEAVRS NEARBY SAY HELLO');
	var gLatLng,
		distance_from_nearby_weavrs,
		nearby_weavrs = [];
		
	$.each(weavrs.nearby, function(index, weavr) {
		
		gLatLng = new GLatLng(weavr.lat, weavr.lon);
		distance_from_nearby_weavrs = weavrs.current_vertex.distanceFrom(gLatLng);
		debug('=============distance from weavr ' + weavr.user + ' = ' + distance_from_nearby_weavrs);
		
		if ((weavr.said_hello_already == false) && (distance_from_nearby_weavrs < weavrs.nearby_weavrs_hello_proximity_threshold)) {
			if ( ! weavrs.nearby_weavr_saying_hello) {
				weavr.said_hello_already = true;
				weavrs.nearby_weavr_saying_hello = weavr.user;
				weavrs.showWeavrsGreetings(weavr);
			}
		}
	});
};


weavrs.showWeavrsGreetings = function (nearby_weavr) {
	debug('>>>>>>>WEAVRS SHOW GREETINGS');
	
	var greeting = weavrs.greetings[Math.floor(Math.random() * weavrs.greetings.length)];
	
	// show greeting
	$('#messages .incoming .fn a').html(nearby_weavr.user.replace(/(_|-)/,' ')).attr('href', nearby_weavr.actions[0].uri);
	$('#messages .incoming .avatar-link').attr('href', nearby_weavr.actions[0].uri);
	
	$('#messages .incoming .avatar').attr('src', nearby_weavr.profile_avatar);
	
	$('#messages .incoming .weavrs-says').html(greeting + ' ' + weavrs.weavr_name.replace(/(_|-)/,' '));
	
	$('#messages').css('display', 'block');
	
	greeting = weavrs.greetings[Math.floor(Math.random() * weavrs.greetings.length)];
	
	// delayed response of current weavr to greeting from nearby weavr and switch to allow next greeting
	setTimeout(function () {
			$('#messages .outgoing .weavrs-says').html(greeting + ' ' + nearby_weavr.user.replace(/(_|-)/,' '));
			$('#messages .outgoing').css('display', 'block');
			// reset to allow for next greeting
			setTimeout(function () {
					$('#messages').css('display','none');
					$('#messages .incoming .avatar').attr('src', '');
					$('#messages .outgoing').css('display','none');
					setTimeout(function () {
							weavrs.nearby_weavr_saying_hello = false;
						}, 
						7000 + (Math.random() * 10000)
					);
				}, 
				9000
			);
		}, 
		2000 + (Math.random() * 2000)
	);

};


/**
* Move forward one link
*/ 
weavrs.advance = function () {
	debug('>>>>>>>WEAVRS ADVANCE');
	/* chose the best link for our current heading */
	
	if (typeof weavrs.pano_meta_data.links === 'undefined') {
		weavrs.advance_timer = setTimeout(function () {weavrs.advance();}, weavrs.advance_delay * 1000);
		return false;
	}
	
	var pan_angle;
	
	weavrs.selected = weavrs.selectLink(weavrs.bearing);
	
	/* If we're very close to a vertex, also check for a
	* link in the direction we should be turning next.
	* If there is a link in that direction (to a
	* tolerance of 15 degrees), chose that turning
	*/
	debug('weavrs.close_to_next_vertex=');
	debug(weavrs.close_to_next_vertex);
	debug('weavrs.next_bearing');
	debug(weavrs.next_bearing);
	if (weavrs.close_to_next_vertex && weavrs.next_bearing) {
		weavrs.selected_turn = weavrs.selectLink(weavrs.next_bearing);
		if (weavrs.selected_turn.delta < 15) {
			weavrs.selected = weavrs.selected_turn;
			weavrs.incrementVertex();
		}
	}
	
	if (weavrs.selected.delta > 40) {
		/* If the chosen link is in a direction more than 40
		* degrees different from the heading we want it
		* will not take us in the right direction. As no
		* better link has been found this implies that the
		* route has no coverage in the direction we need so
		* jump to the start of the next step. 
		*/
		weavrs.jumpToVertex(weavrs.next_vertex_index);
	} else {
		/* Pan the viewer round to face the direction of the
		* link we want to follow and then follow the link. We
		* need to give the pan time to complete before we follow
		* the link for it to look smooth. The amount of time
		* depends on the extent of the pan.
		*/
		pan_angle = getYawDelta(weavrs.pano_meta_data.pov.yaw, weavrs.pano_meta_data.links[weavrs.selected.vertex_index].yaw);
		weavrs.streetview.panTo({ yaw: weavrs.pano_meta_data.links[weavrs.selected.vertex_index].yaw, pitch: 0 });
		setTimeout(
			function() { 
				weavrs.streetview.followLink(weavrs.pano_meta_data.links[weavrs.selected.vertex_index].yaw);
			}, 
			pan_angle * 10
		);
	}
};


/**
* Select which link in the current panorama most closely
* matches the directions we should be going in.
* @param {number} yaw The direction we are looking to move in
* @return {Object} The number of the closest link and the
*  	difference between it's yaw and the desired direction
*/ 
weavrs.selectLink = function (yaw) {
	debug('>>>>>>>WEAVRS SELECT LINK');
	if (typeof weavrs.pano_meta_data.links == 'undefined') {
		return weavrs.selected;
	}
	var i, delta, Selected = new Object();
	
	for (i = 0; i < weavrs.pano_meta_data.links.length; i++) {
		delta = getYawDelta(yaw, weavrs.pano_meta_data.links[i].yaw);
		if (Selected.delta == null || delta < Selected.delta) {
			Selected.vertex_index = i;
			Selected.delta = delta;
		}
	}
	return Selected;
};


/**
* Check if we have already passed the next vertex, or if we are
* close enough to the next vertex to look out for the next turn.
*/ 
weavrs.checkDistanceFromNextVertex = function () {
	debug('>>>>>>>WEAVRS CHECK DISTANCE FROM NEXT VERTEX');
	debug(weavrs.current_vertex);
	debug(weavrs.next_vertex);
	if ( ! weavrs.moving) {
		debug('not checking as not moving');
		return false;
	}
	weavrs.close_to_next_vertex = false;
	var distance = weavrs.current_vertex.distanceFrom(weavrs.next_vertex);
		bearing = getBearing(weavrs.current_vertex, weavrs.next_vertex);
	
	/* If the bearing of the next vertex is more than 90 degrees away from
	* the bearing we have been travelling in, we must have passed it already.
	*/
	if (getYawDelta(weavrs.bearing, bearing) > 90) {
		weavrs.incrementVertex();
		
		/* If the vertices are closely spaced we may
		* already be close to the next vertex
		*/
		weavrs.checkDistanceFromNextVertex();
	} else {
		/* If we are less than 10m from a vertex we consider ourself to be
		* close enough to preferentially follow links that take us in the
		* direction we should be going when the vertex has been passed.
		*/
		if (distance < 10) {
			weavrs.close_to_next_vertex = true;
		}
	}
};


/**
* Called when we have reached a vertex
* and now need to head towards the next
*/
weavrs.incrementVertex = function () {
	debug('>>>>>>>WEAVRS INCREMENT VERTEX');
	if ( ! weavrs.vertices[weavrs.next_vertex_index + 1]) {
		/* we are at the end of the route */
		weavrs.destinationReached();
	} else {
		weavrs.next_vertex_index++;
		weavrs.next_vertex = weavrs.vertices[weavrs.next_vertex_index];
		
		weavrs.bearing = weavrs.getBearingFromVertex(weavrs.next_vertex_index - 1);
		weavrs.next_bearing = weavrs.getBearingFromVertex(weavrs.next_vertex_index);
		
		weavrs.setProgressMarkerImage(weavrs.bearing);
		
		/* Check if we have reached the next step */
		if (weavrs.step_map[weavrs.next_vertex_index - 1] == weavrs.current_step) {
			/* Still on the same step so just extend the
			* progressArray with the next vertex we are
			* heading towards.
			*/
			weavrs.progress_array.push(weavrs.next_vertex);
		} else {
			/* We've moved on to the next step so start a new
			* progressArray and update the text highlight and
			* progress bar.
			*/
			weavrs.current_step = weavrs.step_map[weavrs.next_vertex_index - 1];
			weavrs.progress_array = [ weavrs.current_vertex, weavrs.next_vertex ];
		}
		
		weavrs.setProgressDistance();
	}
};


/**
* Called when the last vertex on the route is reached.
*/
weavrs.destinationReached = function () {
	debug('>>>>>>>WEAVRS ARRIVED AT DESTINATION');
	weavrs.stopMoving();
	weavrs.next_vertex_index = 0;
	weavrs.next_vertex = false;
	weavrs.vertices = new Array();
	weavrs.nextDestination();
};


/**
* Get the direction to head in from a particular vertex
* @param {number} n Index of the vertex in the vertices array
* @return {number} bearing in degrees
*/
weavrs.getBearingFromVertex = function (vertex_index) {
	debug('>>>>>>>WEAVRS GET BEARING FROM VERTEX');
	var origin = weavrs.vertices[vertex_index],
		destination = weavrs.vertices[vertex_index + 1];
	if (destination != undefined) {
		return getBearing(origin, destination);
	} else {
		return null;
	}
};


/**
* Rebuild the progressArray after jumping to a particular vertex
* @param {number} vertexId The vertex number in the vertices array
*/ 
weavrs.constructProgressArray = function (vertexId) {
	debug('>>>>>>>WEAVRS CONSTRUCTING PROGRESS ARRAY');
	weavrs.progress_array = new Array();
	var stepStart = weavrs.step_to_vertex[weavrs.current_step];
	for (var i = weavrs.step_to_vertex[weavrs.current_step]; i <= vertexId + 1; i++) {
		weavrs.progress_array.push(weavrs.vertices[i]);
	}
};

/**
* Calculate the distance in meters from the start of this
* step to the next vertex by building a polyline from the
* intermediate points.
*/
weavrs.setProgressDistance = function () {
	debug('>>>>>>>WEAVRS SET PROGRESS DISTANCE');
	var polyline = new GPolyline(weavrs.progress_array);
	weavrs.progress_distance = polyline.getLength();
	debug('distance travelled = ' + weavrs.progress_distance);
};

/**
* Create a progress marker along the directions path
* @param {GLatLng} 
* @return {GMarker}
*/ 
weavrs.getProgressMarker = function (start) {
	return new GMarker(start, getArrowIcon(0.0));
};

/**
* Set the progress marker along the directions path
* @param {number} bearing The heading in degrees of the arrow we need
*/ 
weavrs.setProgressMarkerImage = function (bearing) {
	weavrs.progress_marker.setImage(getArrowUrl(bearing));
};


//=====================================


weavrs.ajaxComplete = function (jqXHR, textStatus) {
	debug('>>>>>>>WEAVRS AJAX COMPLETE');
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


weavrs.ajaxError = function (jqXHR, textStatus, errorThrown) {
	debug(textStatus);
	debug(errorThrown);
};


// handle cleaning up of previous ajax requests
weavrs.abortPreviousAjaxRequests = function (field) {
	var f;
	if (field === 'all') {
		for (f in weavrs.previous_ajax_requests) {
			if (typeof weavrs.previous_ajax_requests[f].abort == 'function') {
				weavrs.previous_ajax_requests[f].abort();
			}
		}
	} else {
		if (weavrs.previous_ajax_requests[field] !== undefined) {
			if (typeof weavrs.previous_ajax_requests[field].abort == 'function') {
				weavrs.previous_ajax_requests[field].abort();
			}
		}
	}
};


//======================================

/**
* Calculate the difference in degrees between two bearings.
* @param {number} a bearing in degrees
* @param {number} b bearing in degrees
* @return {number} The angle between a and b
*/
function getYawDelta(a, b) {
	var d = Math.abs(sanitiseYaw(a) - sanitiseYaw(b));
	if (d > 180) {
		d = 360 - d;
	}
	return d;
}

/**
* Sometimes after following a link the yaw is > 360
* @param {number} yaw bearing in degrees
* @return {number} yaw as a value between -360 and +360
*/
function sanitiseYaw(yaw) {
	if (yaw > 360 || yaw < 360) {
		yaw = yaw % 360;
	}
	return yaw;
}

/**
* Generate a GMarker icon of an direction arrow
* @param {number} bearing Direction arrow should point
* @return {GIcon}
*/
function getArrowIcon(bearing) {
	var icon = new GIcon();
	icon.image = getArrowUrl(bearing);
	icon.iconSize = new GSize(24, 24);
	icon.iconAnchor = new GPoint(12, 12);
	return icon;
}

/**
* Determine URL of correct direction arrow image to use
* @param {number} bearing Direction arrow should point
* @return {String}
*/
function getArrowUrl(bearing) {
	var id = (3 * Math.round(bearing / 3)) % 120;
	return "http://maps.google.com/mapfiles/dir_" + id + ".png";
}


/**
* Following functions based on those provided at:
* http://www.movable-type.co.uk/scripts/latlong.html
* Copyright 2002-2008 Chris Veness
*/

/**
* Calculate the bearing in degrees between two points
* @param {number} origin  	GLatLng of current location
* @param {number} destination GLatLng of destination
* @return {number}
*/
function getBearing(origin, destination) {
	if (origin.equals(destination)) {
		return null;
	}
	var lat1 = origin.lat().toRad();
	var lat2 = destination.lat().toRad();
	var dLon = (destination.lng()-origin.lng()).toRad();
	
	var y = Math.sin(dLon) * Math.cos(lat2);
	var x = Math.cos(lat1)*Math.sin(lat2) -
  		Math.sin(lat1)*Math.cos(lat2)*Math.cos(dLon);
	return Math.atan2(y, x).toBrng();
}

/**
* Convert an angle in degrees to radians
*/
Number.prototype.toRad = function() {
	return this * Math.PI / 180;
}

/**
* Convert an angle in radians to degrees (signed)
*/
Number.prototype.toDeg = function() {
	return this * 180 / Math.PI;
}

/**
* Convert radians to degrees (as bearing: 0...360)
*/
Number.prototype.toBrng = function() {
	return (this.toDeg()+360) % 360;
}


/**
* Generate a GMarker icon of an direction arrow
* @param {number} bearing Direction arrow should point
* @return {GIcon}
*/
function getArrowIcon(bearing) {
	var icon = new GIcon();
	icon.image = getArrowUrl(bearing);
	icon.iconSize = new GSize(24, 24);
	icon.iconAnchor = new GPoint(12, 12);
	return icon;
}

/**
* Determine URL of correct direction arrow image to use
* @param {number} bearing Direction arrow should point
* @return {String}
*/
function getArrowUrl(bearing) {
	var id = (3 * Math.round(bearing / 3)) % 120;
	return "http://maps.google.com/mapfiles/dir_" + id + ".png";
}