require.config({
	baseUrl: '/static/',
	paths: {
		'app': 'canopsis/core',
		'lib': 'webcore-libs/dev',
		'text': 'webcore-libs/dev/text'
	}
});

require([
	'app/helpers',
	'app/application',
	'app/controller/application',
	'app/controller/accounts',
	'app/controller/groups'
],
function(Application) {
	window.Canopsis = Application;
});