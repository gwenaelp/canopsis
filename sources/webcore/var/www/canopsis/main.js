require.config({
	baseUrl: '/static/',
	paths: {
		'app': 'canopsis/core',
		'lib': 'webcore-libs/dev',
	}
});

require([
	'app/application',
	'app/controller/canopsis',
	'app/view/navbar',
],
function(Application) {
	window.Canopsis = Application;
});