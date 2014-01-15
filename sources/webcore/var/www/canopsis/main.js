require.config({
	baseUrl: '/static/',
	paths: {
		'app': 'core',
		'lib': 'webcore-libs/dev',
	}
});

require([
	'lib/domReady!',
	'app/application'
],
function(domReady, Application) {
});