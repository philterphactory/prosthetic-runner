weavrs.previous_ajax_requests = [];

// called from the LABjs process at the bottom of the base template
weavrs.initPage = function() {
	debug('initializing jswrapper page js');
	$('#api-method-forms-wrapper').delegate(
		'.api-get-results-button',
		'click',
		function (e) {
			debug('get-resuls clicked');
			e.preventDefault();
			var ajax_request,
				$context = $(this).parents('form'),
				method = $context.attr('id'),
				request_method = (method == 'post-write')? 'POST' : 'GET';
			ajax_request = $.ajax({
				type: request_method,
				url: '/jswrapper/api/' + weavrs.weavr_name + '/' + method + '/',
				data: $context.serialize(),
				context: $context,
				//cache: false,
				dataType: 'json',
				success: weavrs.ajaxSuccess,
				error: weavrs.ajaxError,
				complete: weavrs.ajaxComplete
			});
			debug($context);
			weavrs.previous_ajax_requests[$context.attr('id')] = ajax_request;
			return false;
		}
	);
	if (!Modernizr.inputtypes.date) {
		// provide js datepicker 
		$('input[type="date"]').datepicker({dateFormat: 'yy-mm-ddT00:00:00Z'});
	}
};

weavrs.ajaxError = function (jqXHR, textStatus, errorThrown) {
	debug(textStatus);
	debug(errorThrown);
	$('textarea', this).val(JSON.stringify(data));
};

weavrs.ajaxSuccess = function (data, textStatus, jqXHR) {
	debug(textStatus);
	debug(data);
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
