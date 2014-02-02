require.config({
	baseUrl: '/static/',
	paths: {
		'app': 'canopsis/core',
		'lib': 'webcore-libs/dev',
		'text': 'webcore-libs/dev/text',

		'moment': 'webcore-libs/moment.min',
		'jquery': 'webcore-libs/dev/jquery-1.10.2',

		'jquery.encoding.digests.sha1': 'webcore-libs/jQuery.encoding.digests.sha1',
		'jquery.md5': 'webcore-libs/jquery.md5',

		'handlebars': 'webcore-libs/dev/handlebars-1.0.0',
		'ember': 'webcore-libs/dev/ember',
		'ember-data': 'webcore-libs/dev/ember-data',
		'bootstrap': 'webcore-libs/bootstrap/3.0.3/js/bootstrap.min'
	},

	shim: {
		'ember': {
			deps: ['jquery', 'handlebars']
		},

		'ember-data': {
			deps: ['ember']
		},

		'bootstrap': {
			deps: ['jquery']
		}
	}
});

require(['canopsis/main']);
