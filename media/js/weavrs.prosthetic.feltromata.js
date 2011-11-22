weavrs.previous_ajax_requests = {};

weavrs.weavr_configuration = false;

weavrs.current_run_month = 1;

weavrs.current_post_month = 1;

weavrs.weavr_runs = [];
weavrs.weavr_colours = [];
weavrs.weavr_palettes = [];

weavrs.MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'];
weavrs.FROM_LOCAL_STORAGE = 'from localstorage';

// called from the LABjs process at the bottom of the base template
weavrs.initPage = function() {
	debug('>>>>>>>WEAVRS INITIALIZING FELTROMATA');

	weavrs.getConfiguration();
	
	weavrs.getRuns();
};


weavrs.getConfiguration = function () {
	debug('>>>>>>>WEAVRS GET CONFIGURATION OF THIS WEAVR FROM WEAVRS API');
	
	var configuration_data = $.jStorage.get('weavrs_configuration_' + weavrs.weavr_name, false),
		ajax_request;
		
	if (configuration_data !== false) {
		weavrs.getConfigurationSuccess(configuration_data, weavrs.FROM_LOCAL_STORAGE);
	} else {

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
	}
};


weavrs.getConfigurationSuccess = function (data, textStatus, jqXHR) {
	debug('>>>>>>>WEAVRS GET CONFIGURATION SUCCESS');
	debug(textStatus);
	debug(data);

	weavrs.weavr_configuration = data;
	
	if (textStatus != weavrs.FROM_LOCAL_STORAGE) {
		// add a counter to the emotion array in the returned config to be incremented when iterating through the run data 
		if (typeof weavrs.weavr_configuration.emotions != 'undefined') {
			$.each(weavrs.weavr_configuration.emotions, function (index, emotion) {
				weavrs.weavr_configuration.emotions[index].totals = {total:0, monthly_totals: [0,0,0,0,0,0,0,0,0,0,0,0]};
				weavrs.weavr_configuration.emotion_totals_calculated = false;
			});
		}
	
		$.jStorage.set('weavrs_configuration_' + weavrs.weavr_name, data);
	}
	
	debug(weavrs.weavr_configuration);
	
	$('#main-weavrs-info .avatar').attr('src', weavrs.hub_url + 'api/weavrs/' + weavrs.weavr_configuration.id + '/avatar_current_image.png');
	$('#main-weavrs-info .address').html(weavrs.weavr_configuration.home_address);
	$('#main-weavrs-info .fn').attr('href', weavrs.weavr_configuration.blog).html(weavrs.weavr_name.replace(/(_|-)/,' '));
	$('#avatar-link').attr('href', weavrs.weavr_configuration.blog);
	
	weavrs.displayEmotionalRange();
};


weavrs.displayEmotionalRange = function () {

};


weavrs.getRuns = function () {
	debug('>>>>>>>WEAVRS GET RUNS OF THIS WEAVR FROM WEAVRS API');
	var run_data = $.jStorage.get('weavrs_runs_' + weavrs.weavr_name, false);
	
	if (run_data !== false) {
		weavrs.getRunsSuccess(run_data, weavrs.FROM_LOCAL_STORAGE);
	} else {
		var ajax_request, 
			current_month = (weavrs.current_run_month < 10)? '0' + weavrs.current_run_month : '' + weavrs.current_run_month,
			days_in_month = 32 - (new Date('2011', weavrs.current_run_month - 1, 32).getDate());
	
		ajax_request = $.ajax({
			url: '/jswrapper/api/' + weavrs.weavr_name + '/run/?after=2011-' + current_month + '-01T00:00:00Z&before=2011-' + current_month + '-' + days_in_month + 'T23:59:00Z&per_page=20&posts=true',
			type: 'GET',
			//cache: false,
			dataType: 'json',
			success: weavrs.getRunsSuccess,
			error: weavrs.ajaxError,
			complete: weavrs.ajaxComplete
		});
		
		weavrs.previous_ajax_requests.get_runs = ajax_request;
	}
};


weavrs.getRunsSuccess = function (data, textStatus, jqXHR) {
	debug('>>>>>>>WEAVRS GET RUNS SUCCESS');
	debug(textStatus);
	debug(data);
	
	if (textStatus == weavrs.FROM_LOCAL_STORAGE) {
		weavrs.weavr_runs = data;
		
		// if the config has been loaded from localstorage there's no need to repeat the emotion counts
		if ( ! weavrs.weavr_configuration.emotion_totals_calculated) {
			weavrs.countEmotionTotals();
		}
		
		weavrs.collectColours();
		
		weavrs.drawEmotionPie();
		
	} else {
		
		weavrs.weavr_runs.push(data);
		
		weavrs.current_run_month++;
		if (weavrs.current_run_month < 13) {
			weavrs.getRuns();
		} else {
			debug('>>>>>>>RUNS COMPLETE');
			
			$.jStorage.set('weavrs_runs_'  + weavrs.weavr_name, weavrs.weavr_runs);
			
			// if the config has been loaded from localstorage there's no need to repeat the emotion counts
			if ( ! weavrs.weavr_configuration.emotion_totals_calculated) {
				weavrs.countEmotionTotals();
			}

			weavrs.collectColours();
			
			weavrs.drawEmotionPie();
		}
	}

};


weavrs.countEmotionTotals = function () {
	debug('>>>>>>>WEAVRS COUNTING EMOTIONAL TOTALS');
	
	$.each(weavrs.weavr_runs, function(m_i, runs_in_month) {
		$.each(runs_in_month.runs, function (r_i, run) {
			$.each(weavrs.weavr_configuration.emotions, function (e_i, c_emotion) {
				if (c_emotion.emotion == run.emotion) {
					weavrs.weavr_configuration.emotions[e_i].totals.total += 1;
					weavrs.weavr_configuration.emotions[e_i].totals.monthly_totals[m_i] += 1;
				}
			});
		});
	});

	weavrs.weavr_configuration.emotions.sort(weavrs.emotionComparator);
	debug(weavrs.weavr_configuration.emotions);
	$.jStorage.set('weavrs_configuration_' + weavrs.weavr_name, weavrs.weavr_configuration);
	
	debug(weavrs.weavr_configuration);
};

weavrs.emotionComparator = function(a,b) {
	return b.totals.total - a.totals.total;
};


weavrs.collectColours = function () {
	debug('>>>>>>>WEAVRS COLLECTING COLOURS');
	var colours,
		palette,
		emotion,
		valid,
		temp_palettes = {},
		temp_colours = {};
	
	$.each(weavrs.weavr_runs, function (m, monthly_runs) {
	
		$.each(monthly_runs.runs, function (r, run) {

			emotion = run.emotion;

			$.each(run.posts, function (p, post) {

				//image_url example http://www.colourlovers.com/paletteImg/6B6800/7C9906/492C24/532E24/4D4107/Ent_Moot.png

				if (post.category == 'palette') {
					colours = post.image_url.replace('http://www.colourlovers.com/paletteImg/','');
					colours = colours.split('/');
					colours.pop();
					palette = colours.join('_');
					
					if ( ! (palette in temp_palettes)) {
						temp_palettes[palette] = {total:0, monthly_totals: [0,0,0,0,0,0,0,0,0,0,0,0], colours: colours, emotions: {}, source_url:'', source_user_name:'', title:''};
					}
					if ( ! (emotion in temp_palettes[palette].emotions)) {
						temp_palettes[palette].emotions[emotion] = {total:0, monthly_totals: [0,0,0,0,0,0,0,0,0,0,0,0]};
					}
					temp_palettes[palette].colours = [];
					temp_palettes[palette].title = post.title;
					temp_palettes[palette].source_url = post.source_url;
					temp_palettes[palette].source_user_name = post.source_user_name;
					temp_palettes[palette].total += 1;
					temp_palettes[palette].monthly_totals[m] += 1;
					temp_palettes[palette].emotions[emotion].total += 1;
					temp_palettes[palette].emotions[emotion].monthly_totals[m] += 1;
					//debug(weavrs.weavr_palettes);

					$.each(colours, function (c, colour) {

						valid = colour.match(/^[0-9a-fA-F]{6}$/);
						//debug(valid);
						//debug(colour);
						if (valid) {
							valid = valid[0];
							if ( ! (valid in temp_colours)) {
								temp_colours[valid] = {total:0, monthly_totals: [0,0,0,0,0,0,0,0,0,0,0,0], emotions: {}};
							}
							if ( ! (emotion in temp_colours[valid].emotions)) {
								temp_colours[valid].emotions[emotion] = {total:0, monthly_totals: [0,0,0,0,0,0,0,0,0,0,0,0]};
							}
							temp_colours[valid].hex = valid;
							temp_colours[valid].total += 1;
							temp_colours[valid].monthly_totals[m] += 1;
							temp_colours[valid].emotions[emotion].total += 1;
							temp_colours[valid].emotions[emotion].monthly_totals[m] += 1;
							if ( ! $.inArray(valid, temp_palettes[palette].colours)) {
								temp_palettes[palette].colours.push(valid);
							}
						}
					});
				}
			});
		});
	});
	
	// now order the palettes and colours by frequency
	$.each(temp_palettes, function (p, palette) {
		weavrs.weavr_palettes.push(palette);
	});
	
	$.each(temp_colours, function (c, colour) {
		weavrs.weavr_colours.push(colour);
	});
	weavrs.weavr_palettes.sort(weavrs.colour_comparator);
	weavrs.weavr_colours.sort(weavrs.colour_comparator);
	
	$.each(weavrs.colour_comparator, function (i, colour) {
		$('#colours ul').append('<li class="colour-ball" style="background-colour:#' + colour.hex + '; width: ' + (colour.total * 10) + 'px; height: ' + (colour.total * 10) + 'px;"></li>');
	});
};

weavrs.colour_comparator = function (a,b) {
	return b.total - a.total;
};


weavrs.drawEmotionPie = function () {
	if ( ! google_charts_loaded) {
		setTimeout(function () {weavrs.drawEmotionPie();}, 1000);
		return false;
	}
	
	var emotion_pie,
		emotions,
		colours = [],
		pie_width = 120;
		pie_height = 120;
	
	// populate yearly emotion data table 
	emotions = new google.visualization.DataTable();
	emotions.addColumn('string', 'Emotion');
	emotions.addColumn('number', 'Proportion Of Time Spent feeling This Way');
	emotions.addRows(weavrs.weavr_configuration.emotions.length);
	$.each(weavrs.weavr_configuration.emotions, function(e_i, c_emotion) {
		emotions.setValue(e_i, 0, c_emotion.emotion);
		emotions.setValue(e_i, 1, c_emotion.totals.total);
		colours.push('#' + weavrs.weavr_colours[e_i].hex);
	});
	
	// draw yearly emotion pie
	emotion_pie = new google.visualization.PieChart(document.getElementById('yearly-emotions'));
	emotion_pie.draw(emotions, {width: 450, height: 250, title: 'My Feelings This Year', tooltipText: 'value', tooltipTextStyle: {color: 'black', fontName: 'helvetica', fontSize: 15}, colors: colours, is3D: true, legendTextStyle: {color: 'black', fontName: 'helvetica', fontSize: 15}, pieSliceText: 'none', chartArea: {left:0,top:0,width:"100%",height:"100%"}});
	
	// populate monthly emotion data tables and draw emotion pies
	for (m in weavrs.MONTHS) {
		emotions = new google.visualization.DataTable();
		emotions.addColumn('string', 'Emotion');
		emotions.addColumn('number', 'Proportion Of Time Spent feeling This Way');
		emotions.addRows(weavrs.weavr_configuration.emotions.length);
		
		colours = [];
		$.each(weavrs.weavr_configuration.emotions, function (e_i, c_emotion) {
			emotions.setValue(e_i, 0, c_emotion.emotion);
			emotions.setValue(e_i, 1, c_emotion.totals.monthly_totals[m]);
			colours.push('#' + weavrs.weavr_colours[e_i].hex);
		});
		// draw monthly emotion pie
		emotion_pie = new google.visualization.PieChart($('#emotions .months .' + weavrs.MONTHS[m] + ' .monthly-emotions').get(0));
		emotion_pie.draw(emotions, {width: pie_width, height: pie_height, title: '', tooltipText: 'value', tooltipTextStyle: {color: 'black', fontName: 'helvetica', fontSize: 15}, colors: colours, is3D: true, legend: 'none', pieSliceText: 'none', chartArea: {left:5,top:0,width:"100%",height:"100%"}});
	}
};

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