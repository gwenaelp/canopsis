define(function(require, exports, module) {
	var Application = require('app/application');
	require('app/controller/navbar');

	Ember.TEMPLATES['navbar'] = Ember.Handlebars.compile(require('app/text!app/templates/navbar.html'));

	Application.NavbarView = Ember.View.extend({
		templateName: 'navbar',
		meta: {
			title: 'Canopsis',
			menu: [
				{
					name: 'Build',
					links: [
						{url: 'build/accounts', title: 'Accounts'},
						{url: 'build/groups', title: 'Groups'},
						{url: 'build/curves', title: 'Curves'},
						{url: 'build/perfdata', title: 'PerfData'}
					]
				},
				{
					name: 'Run',
					links: [
						{url: 'run/dashboard', title: 'Dashboard'}
					]
				}
			]
		}
	});
});