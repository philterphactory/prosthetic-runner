function debug(msg)
{
	if (weavrs.debug)
	{
		if ((typeof console) === 'object')
		{
			// use firebug for debug output
			console.log(msg);
		}
		else
		{
			/*if ($('body #debugger').length < 1)
			{
				$('body').append('<div id="debugger"> </div>');
			}

			$('body #debugger').append('<p class="debug message">'+msg+'</p>');*/
		}
	}
}