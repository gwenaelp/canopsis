define([
	'canopsis/commit',
	'jquery',
	'bootstrap',
	'app/lib/helpers',
	'app/lib/templates',
	'app/application',
	'app/controller/login',
	'app/controller/application',
	'app/controller/accounts',
	'app/controller/groups',
	'app/controller/curves',
	'app/controller/perfdata',
	'app/controller/selectors',
	'app/controller/consolidation',
	'app/view/login',
	'app/view/application',
	'app/view/accounts'
], function(commit, $, _bootstrap, _helpers, _tmpls, Application) {
	window.Canopsis = Application;
	Canopsis.commit = commit;
});