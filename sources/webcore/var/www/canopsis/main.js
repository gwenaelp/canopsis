define([
	'jquery',
	'bootstrap',
	'app/lib/helpers',
	'app/lib/templates',
	'app/application',
	'app/controller/application',
	'app/controller/accounts',
	'app/controller/groups',
	'app/controller/curves',
	'app/controller/perfdata',
	'app/controller/selectors',
	'app/controller/consolidation'
], function($, _bootstrap, _helpers, _tmpls, Application) {
	window.Canopsis = Application;
});