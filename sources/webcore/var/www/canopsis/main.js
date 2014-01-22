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
	'app/controller/groups',
	'app/controller/curves',
	'app/controller/perfdata',
	'app/controller/selectors',
	'app/controller/consolidation'
],
function(Application) {
	window.Canopsis = Application;
});